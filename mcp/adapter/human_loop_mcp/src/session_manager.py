"""
Human-in-the-Loop MCP 会话管理器
负责管理交互会话的生命周期、状态和持久化
"""

import json
import sqlite3
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
import logging
import redis
from contextlib import contextmanager

from models import InteractionSession, SessionStatus, InteractionData


class SessionManager:
    """会话管理器"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # 内存中的活跃会话
        self.active_sessions: Dict[str, InteractionSession] = {}
        self.session_lock = threading.RLock()
        
        # Redis连接
        self.redis_client = None
        if config.get('redis', {}).get('host'):
            try:
                self.redis_client = redis.Redis(
                    host=config['redis']['host'],
                    port=config['redis']['port'],
                    db=config['redis']['db'],
                    decode_responses=True
                )
                self.redis_client.ping()
                self.logger.info("Redis连接成功")
            except Exception as e:
                self.logger.warning(f"Redis连接失败: {e}")
                self.redis_client = None
        
        # SQLite数据库
        self.db_path = config['database']['path']
        self.init_database()
        
        # 回调函数
        self.session_callbacks: Dict[str, Callable] = {}
        
        # 启动清理线程
        self.cleanup_interval = config['session']['cleanup_interval']
        self.cleanup_thread = threading.Thread(target=self._cleanup_expired_sessions, daemon=True)
        self.cleanup_thread.start()
        
        self.logger.info("会话管理器初始化完成")
    
    def init_database(self):
        """初始化SQLite数据库"""
        with self.get_db_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    workflow_id TEXT,
                    callback_url TEXT,
                    interaction_data TEXT,
                    status TEXT,
                    created_at TEXT,
                    updated_at TEXT,
                    expires_at TEXT,
                    response_data TEXT,
                    error_message TEXT
                )
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_sessions_status 
                ON sessions(status)
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_sessions_workflow 
                ON sessions(workflow_id)
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_sessions_expires 
                ON sessions(expires_at)
            ''')
            
            conn.commit()
    
    @contextmanager
    def get_db_connection(self):
        """获取数据库连接的上下文管理器"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def create_session(self, interaction_data: InteractionData, 
                      workflow_id: str = None, callback_url: str = None) -> InteractionSession:
        """创建新的交互会话"""
        session = InteractionSession(
            interaction_data=interaction_data,
            workflow_id=workflow_id,
            callback_url=callback_url
        )
        
        with self.session_lock:
            # 添加到内存
            self.active_sessions[session.session_id] = session
            
            # 保存到Redis
            if self.redis_client:
                try:
                    self.redis_client.setex(
                        f"session:{session.session_id}",
                        interaction_data.timeout,
                        json.dumps(session.to_dict())
                    )
                except Exception as e:
                    self.logger.warning(f"Redis保存失败: {e}")
            
            # 保存到数据库
            self._save_session_to_db(session)
        
        self.logger.info(f"创建会话: {session.session_id}")
        return session
    
    def get_session(self, session_id: str) -> Optional[InteractionSession]:
        """获取会话"""
        with self.session_lock:
            # 先从内存查找
            if session_id in self.active_sessions:
                return self.active_sessions[session_id]
            
            # 从Redis查找
            if self.redis_client:
                try:
                    session_data = self.redis_client.get(f"session:{session_id}")
                    if session_data:
                        session = InteractionSession.from_dict(json.loads(session_data))
                        self.active_sessions[session_id] = session
                        return session
                except Exception as e:
                    self.logger.warning(f"Redis读取失败: {e}")
            
            # 从数据库查找
            session = self._load_session_from_db(session_id)
            if session:
                self.active_sessions[session_id] = session
            
            return session
    
    def update_session(self, session: InteractionSession):
        """更新会话"""
        with self.session_lock:
            # 更新内存
            self.active_sessions[session.session_id] = session
            
            # 更新Redis
            if self.redis_client:
                try:
                    remaining_time = max(0, int((session.expires_at - datetime.now()).total_seconds()))
                    if remaining_time > 0:
                        self.redis_client.setex(
                            f"session:{session.session_id}",
                            remaining_time,
                            json.dumps(session.to_dict())
                        )
                    else:
                        self.redis_client.delete(f"session:{session.session_id}")
                except Exception as e:
                    self.logger.warning(f"Redis更新失败: {e}")
            
            # 更新数据库
            self._save_session_to_db(session)
        
        self.logger.info(f"更新会话: {session.session_id}, 状态: {session.status.value}")
    
    def complete_session(self, session_id: str, response_data: Dict, user_id: str = None) -> bool:
        """完成会话"""
        session = self.get_session(session_id)
        if not session:
            self.logger.error(f"会话不存在: {session_id}")
            return False
        
        if session.status != SessionStatus.PENDING:
            self.logger.error(f"会话状态无效: {session_id}, 当前状态: {session.status.value}")
            return False
        
        # 设置响应
        session.set_response(response_data, user_id)
        self.update_session(session)
        
        # 执行回调
        if session.session_id in self.session_callbacks:
            try:
                callback = self.session_callbacks[session.session_id]
                callback(session)
                del self.session_callbacks[session.session_id]
            except Exception as e:
                self.logger.error(f"回调执行失败: {e}")
        
        # 从活跃会话中移除
        with self.session_lock:
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
        
        self.logger.info(f"完成会话: {session_id}")
        return True
    
    def cancel_session(self, session_id: str, reason: str = None) -> bool:
        """取消会话"""
        session = self.get_session(session_id)
        if not session:
            return False
        
        session.update_status(SessionStatus.CANCELLED, reason)
        self.update_session(session)
        
        # 从活跃会话中移除
        with self.session_lock:
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
        
        self.logger.info(f"取消会话: {session_id}, 原因: {reason}")
        return True
    
    def get_active_sessions(self) -> List[InteractionSession]:
        """获取所有活跃会话"""
        with self.session_lock:
            return list(self.active_sessions.values())
    
    def get_sessions_by_workflow(self, workflow_id: str) -> List[InteractionSession]:
        """根据工作流ID获取会话"""
        sessions = []
        with self.get_db_connection() as conn:
            cursor = conn.execute(
                'SELECT * FROM sessions WHERE workflow_id = ? ORDER BY created_at DESC',
                (workflow_id,)
            )
            for row in cursor:
                session = self._row_to_session(row)
                if session:
                    sessions.append(session)
        return sessions
    
    def register_callback(self, session_id: str, callback: Callable):
        """注册会话完成回调"""
        self.session_callbacks[session_id] = callback
    
    def _save_session_to_db(self, session: InteractionSession):
        """保存会话到数据库"""
        try:
            with self.get_db_connection() as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO sessions 
                    (session_id, workflow_id, callback_url, interaction_data, status,
                     created_at, updated_at, expires_at, response_data, error_message)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    session.session_id,
                    session.workflow_id,
                    session.callback_url,
                    json.dumps(session.interaction_data.to_dict()) if session.interaction_data else None,
                    session.status.value,
                    session.created_at.isoformat(),
                    session.updated_at.isoformat(),
                    session.expires_at.isoformat(),
                    json.dumps(session.response.to_dict()) if session.response else None,
                    session.error_message
                ))
                conn.commit()
        except Exception as e:
            self.logger.error(f"数据库保存失败: {e}")
    
    def _load_session_from_db(self, session_id: str) -> Optional[InteractionSession]:
        """从数据库加载会话"""
        try:
            with self.get_db_connection() as conn:
                cursor = conn.execute(
                    'SELECT * FROM sessions WHERE session_id = ?',
                    (session_id,)
                )
                row = cursor.fetchone()
                if row:
                    return self._row_to_session(row)
        except Exception as e:
            self.logger.error(f"数据库读取失败: {e}")
        return None
    
    def _row_to_session(self, row) -> Optional[InteractionSession]:
        """将数据库行转换为会话对象"""
        try:
            session_data = {
                'session_id': row['session_id'],
                'workflow_id': row['workflow_id'],
                'callback_url': row['callback_url'],
                'status': row['status'],
                'created_at': row['created_at'],
                'updated_at': row['updated_at'],
                'expires_at': row['expires_at'],
                'error_message': row['error_message']
            }
            
            if row['interaction_data']:
                session_data['interaction_data'] = json.loads(row['interaction_data'])
            
            if row['response_data']:
                session_data['response'] = json.loads(row['response_data'])
            
            return InteractionSession.from_dict(session_data)
        except Exception as e:
            self.logger.error(f"会话数据解析失败: {e}")
            return None
    
    def _cleanup_expired_sessions(self):
        """清理过期会话的后台线程"""
        while True:
            try:
                current_time = datetime.now()
                expired_sessions = []
                
                with self.session_lock:
                    for session_id, session in list(self.active_sessions.items()):
                        if session.is_expired():
                            expired_sessions.append(session_id)
                
                # 处理过期会话
                for session_id in expired_sessions:
                    session = self.get_session(session_id)
                    if session and session.status == SessionStatus.PENDING:
                        session.update_status(SessionStatus.TIMEOUT)
                        self.update_session(session)
                        
                        # 从活跃会话中移除
                        with self.session_lock:
                            if session_id in self.active_sessions:
                                del self.active_sessions[session_id]
                        
                        self.logger.info(f"会话超时: {session_id}")
                
                # 清理Redis中的过期键
                if self.redis_client and expired_sessions:
                    try:
                        keys_to_delete = [f"session:{sid}" for sid in expired_sessions]
                        self.redis_client.delete(*keys_to_delete)
                    except Exception as e:
                        self.logger.warning(f"Redis清理失败: {e}")
                
                time.sleep(self.cleanup_interval)
                
            except Exception as e:
                self.logger.error(f"清理线程异常: {e}")
                time.sleep(self.cleanup_interval)
    
    def get_statistics(self) -> Dict:
        """获取会话统计信息"""
        stats = {
            'active_sessions': len(self.active_sessions),
            'total_sessions': 0,
            'completed_sessions': 0,
            'timeout_sessions': 0,
            'cancelled_sessions': 0
        }
        
        try:
            with self.get_db_connection() as conn:
                # 总会话数
                cursor = conn.execute('SELECT COUNT(*) FROM sessions')
                stats['total_sessions'] = cursor.fetchone()[0]
                
                # 各状态会话数
                cursor = conn.execute('''
                    SELECT status, COUNT(*) FROM sessions 
                    GROUP BY status
                ''')
                for row in cursor:
                    status, count = row
                    if status == SessionStatus.COMPLETED.value:
                        stats['completed_sessions'] = count
                    elif status == SessionStatus.TIMEOUT.value:
                        stats['timeout_sessions'] = count
                    elif status == SessionStatus.CANCELLED.value:
                        stats['cancelled_sessions'] = count
        except Exception as e:
            self.logger.error(f"统计信息获取失败: {e}")
        
        return stats

