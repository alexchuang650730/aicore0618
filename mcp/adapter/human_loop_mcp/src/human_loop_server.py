"""
Human-in-the-Loop MCP API服务器
提供RESTful API接口和WebSocket实时通信
"""

import os
import sys
import json
import yaml
import logging
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
from flask import Flask, jsonify, request, send_from_directory, render_template_string
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
import requests
import threading

# 添加项目路径
sys.path.append('/home/ubuntu/aicore0615')

from models import InteractionData, InteractionType, InteractionField, InteractionTemplates, CommonFields
from session_manager import SessionManager


class HumanLoopMCPServer:
    """Human-in-the-Loop MCP服务器"""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or "/home/ubuntu/aicore0615/mcp/adapter/human_loop_mcp/config/human_loop_mcp_config.yaml"
        self.config = self.load_config()
        
        # 设置日志
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # 创建Flask应用
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = self.config['security']['session_secret']
        
        # 启用CORS
        CORS(self.app, origins=self.config['security']['cors_origins'])
        
        # 创建SocketIO
        self.socketio = SocketIO(self.app, cors_allowed_origins=self.config['security']['cors_origins'])
        
        # 初始化会话管理器
        self.session_manager = SessionManager(self.config)
        
        # 注册路由
        self.register_routes()
        self.register_websocket_events()
        
        self.logger.info("Human-in-the-Loop MCP服务器初始化完成")
    
    def load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"配置文件加载失败: {e}")
            # 返回默认配置
            return {
                'server': {'host': '0.0.0.0', 'port': 8096, 'debug': False},
                'security': {'cors_origins': ['*'], 'session_secret': 'default-secret'},
                'session': {'default_timeout': 300, 'max_timeout': 3600, 'cleanup_interval': 60},
                'database': {'type': 'sqlite', 'path': 'data/human_loop.db'},
                'redis': {'host': 'localhost', 'port': 6379, 'db': 5},
                'logging': {'level': 'INFO', 'file': 'logs/human_loop_mcp.log'}
            }
    
    def setup_logging(self):
        """设置日志"""
        log_level = getattr(logging, self.config['logging']['level'].upper())
        log_file = self.config['logging']['file']
        
        # 确保日志目录存在
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
    
    def register_routes(self):
        """注册API路由"""
        
        @self.app.route('/')
        def index():
            """主页面"""
            return send_from_directory('../frontend', 'index.html')
        
        @self.app.route('/api/health')
        def health_check():
            """健康检查"""
            stats = self.session_manager.get_statistics()
            return jsonify({
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "version": self.config['service']['version'],
                "service": self.config['service']['name'],
                "statistics": stats
            })
        
        @self.app.route('/api/sessions', methods=['POST'])
        def create_session():
            """创建新的交互会话"""
            try:
                data = request.get_json()
                
                # 验证必需字段
                if not data or 'interaction_data' not in data:
                    return jsonify({"error": "缺少interaction_data字段"}), 400
                
                interaction_data_dict = data['interaction_data']
                
                # 解析交互类型
                try:
                    interaction_type = InteractionType(interaction_data_dict['interaction_type'])
                except ValueError:
                    return jsonify({"error": "无效的交互类型"}), 400
                
                # 解析字段
                fields = None
                if 'fields' in interaction_data_dict and interaction_data_dict['fields']:
                    fields = [InteractionField(**field) for field in interaction_data_dict['fields']]
                
                # 创建交互数据
                interaction_data = InteractionData(
                    interaction_type=interaction_type,
                    title=interaction_data_dict['title'],
                    message=interaction_data_dict['message'],
                    fields=fields,
                    options=interaction_data_dict.get('options'),
                    default_value=interaction_data_dict.get('default_value'),
                    timeout=interaction_data_dict.get('timeout', self.config['session']['default_timeout']),
                    multiple=interaction_data_dict.get('multiple', False),
                    accept_types=interaction_data_dict.get('accept_types'),
                    max_file_size=interaction_data_dict.get('max_file_size')
                )
                
                # 创建会话
                session = self.session_manager.create_session(
                    interaction_data=interaction_data,
                    workflow_id=data.get('workflow_id'),
                    callback_url=data.get('callback_url')
                )
                
                # 通知前端有新会话
                self.socketio.emit('new_session', session.to_dict(), room='ui_clients')
                
                return jsonify({
                    "success": True,
                    "session_id": session.session_id,
                    "session": session.to_dict()
                })
                
            except Exception as e:
                self.logger.error(f"创建会话失败: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/sessions/<session_id>', methods=['GET'])
        def get_session(session_id):
            """获取会话信息"""
            try:
                session = self.session_manager.get_session(session_id)
                if not session:
                    return jsonify({"error": "会话不存在"}), 404
                
                return jsonify({
                    "success": True,
                    "session": session.to_dict()
                })
                
            except Exception as e:
                self.logger.error(f"获取会话失败: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/sessions/<session_id>/respond', methods=['POST'])
        def respond_session(session_id):
            """提交用户响应"""
            try:
                data = request.get_json()
                if not data or 'response' not in data:
                    return jsonify({"error": "缺少response字段"}), 400
                
                success = self.session_manager.complete_session(
                    session_id=session_id,
                    response_data=data['response'],
                    user_id=data.get('user_id')
                )
                
                if not success:
                    return jsonify({"error": "会话响应失败"}), 400
                
                # 获取更新后的会话
                session = self.session_manager.get_session(session_id)
                
                # 通知前端会话已完成
                self.socketio.emit('session_completed', {
                    'session_id': session_id,
                    'session': session.to_dict() if session else None
                }, room='ui_clients')
                
                # 如果有回调URL，发送回调
                if session and session.callback_url:
                    self.send_callback(session)
                
                return jsonify({
                    "success": True,
                    "message": "响应已提交"
                })
                
            except Exception as e:
                self.logger.error(f"提交响应失败: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/sessions/<session_id>/cancel', methods=['POST'])
        def cancel_session(session_id):
            """取消会话"""
            try:
                data = request.get_json() or {}
                reason = data.get('reason', '用户取消')
                
                success = self.session_manager.cancel_session(session_id, reason)
                if not success:
                    return jsonify({"error": "会话取消失败"}), 400
                
                # 通知前端会话已取消
                self.socketio.emit('session_cancelled', {
                    'session_id': session_id,
                    'reason': reason
                }, room='ui_clients')
                
                return jsonify({
                    "success": True,
                    "message": "会话已取消"
                })
                
            except Exception as e:
                self.logger.error(f"取消会话失败: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/sessions', methods=['GET'])
        def list_sessions():
            """获取会话列表"""
            try:
                workflow_id = request.args.get('workflow_id')
                
                if workflow_id:
                    sessions = self.session_manager.get_sessions_by_workflow(workflow_id)
                else:
                    sessions = self.session_manager.get_active_sessions()
                
                return jsonify({
                    "success": True,
                    "sessions": [session.to_dict() for session in sessions]
                })
                
            except Exception as e:
                self.logger.error(f"获取会话列表失败: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/statistics')
        def get_statistics():
            """获取统计信息"""
            try:
                stats = self.session_manager.get_statistics()
                return jsonify({
                    "success": True,
                    "statistics": stats
                })
                
            except Exception as e:
                self.logger.error(f"获取统计信息失败: {e}")
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/templates')
        def get_templates():
            """获取交互模板"""
            templates = {
                "confirmation": {
                    "name": "确认对话框",
                    "description": "用于需要用户确认的场景",
                    "example": InteractionTemplates.confirmation(
                        "确认操作", "是否继续执行？"
                    ).to_dict()
                },
                "selection": {
                    "name": "选择对话框", 
                    "description": "用于需要用户从多个选项中选择的场景",
                    "example": InteractionTemplates.selection(
                        "选择环境", "请选择部署环境",
                        [{"value": "dev", "label": "开发环境"}]
                    ).to_dict()
                },
                "text_input": {
                    "name": "文本输入",
                    "description": "用于需要用户输入文本信息的场景", 
                    "example": InteractionTemplates.text_input(
                        "输入配置", "请输入配置参数",
                        [CommonFields.text_field("name", "名称", True)]
                    ).to_dict()
                },
                "file_upload": {
                    "name": "文件上传",
                    "description": "用于需要用户上传文件的场景",
                    "example": InteractionTemplates.file_upload(
                        "上传文件", "请上传配置文件"
                    ).to_dict()
                }
            }
            
            return jsonify({
                "success": True,
                "templates": templates
            })
    
    def register_websocket_events(self):
        """注册WebSocket事件"""
        
        @self.socketio.on('connect')
        def handle_connect():
            """客户端连接"""
            self.logger.info(f"客户端连接: {request.sid}")
            join_room('ui_clients')
            emit('connected', {'message': '连接成功'})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            """客户端断开连接"""
            self.logger.info(f"客户端断开连接: {request.sid}")
            leave_room('ui_clients')
        
        @self.socketio.on('join_session')
        def handle_join_session(data):
            """加入会话房间"""
            session_id = data.get('session_id')
            if session_id:
                join_room(f'session_{session_id}')
                emit('joined_session', {'session_id': session_id})
        
        @self.socketio.on('leave_session')
        def handle_leave_session(data):
            """离开会话房间"""
            session_id = data.get('session_id')
            if session_id:
                leave_room(f'session_{session_id}')
                emit('left_session', {'session_id': session_id})
    
    def send_callback(self, session):
        """发送回调通知"""
        if not session.callback_url:
            return
        
        def send_async():
            try:
                callback_data = {
                    'session_id': session.session_id,
                    'workflow_id': session.workflow_id,
                    'status': session.status.value,
                    'response': session.response.to_dict() if session.response else None,
                    'timestamp': datetime.now().isoformat()
                }
                
                response = requests.post(
                    session.callback_url,
                    json=callback_data,
                    timeout=self.config['integration']['workflow_callback_timeout']
                )
                
                if response.status_code == 200:
                    self.logger.info(f"回调发送成功: {session.session_id}")
                else:
                    self.logger.warning(f"回调响应异常: {response.status_code}")
                    
            except Exception as e:
                self.logger.error(f"回调发送失败: {e}")
        
        # 异步发送回调
        threading.Thread(target=send_async, daemon=True).start()
    
    def run(self):
        """启动服务器"""
        host = self.config['server']['host']
        port = self.config['server']['port']
        debug = self.config['server']['debug']
        
        self.logger.info(f"启动Human-in-the-Loop MCP服务器: {host}:{port}")
        
        self.socketio.run(
            self.app,
            host=host,
            port=port,
            debug=debug,
            allow_unsafe_werkzeug=True
        )


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Human-in-the-Loop MCP服务器')
    parser.add_argument('--config', '-c', 
                       default='/home/ubuntu/aicore0615/mcp/adapter/human_loop_mcp/config/human_loop_mcp_config.yaml',
                       help='配置文件路径')
    
    args = parser.parse_args()
    
    # 创建必要的目录
    os.makedirs('/home/ubuntu/aicore0615/mcp/adapter/human_loop_mcp/logs', exist_ok=True)
    os.makedirs('/home/ubuntu/aicore0615/mcp/adapter/human_loop_mcp/data', exist_ok=True)
    
    # 启动服务器
    server = HumanLoopMCPServer(args.config)
    server.run()


if __name__ == '__main__':
    main()

