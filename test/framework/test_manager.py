#!/usr/bin/env python3
"""
PowerAutomation 中央测试管理器
负责统一管理和协调所有测试活动
"""

import asyncio
import logging
import json
import yaml
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
import concurrent.futures
import threading
import time

from .test_discovery import TestDiscovery
from .test_runner import TestRunner
from .test_reporter import TestReporter
from .test_scheduler import TestScheduler

@dataclass
class TestResult:
    """测试结果数据类"""
    test_id: str
    test_name: str
    module_name: str
    test_type: str
    status: str  # PASS, FAIL, ERROR, SKIP
    duration: float
    start_time: datetime
    end_time: datetime
    error_message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

@dataclass
class TestSession:
    """测试会话数据类"""
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    error_tests: int = 0
    skipped_tests: int = 0
    results: List[TestResult] = None
    
    def __post_init__(self):
        if self.results is None:
            self.results = []

class TestManager:
    """
    PowerAutomation 中央测试管理器
    
    功能:
    - 统一管理所有测试
    - 协调测试执行
    - 管理测试会话
    - 提供测试API
    """
    
    def __init__(self, config_path: Optional[str] = None):
        self.project_root = Path("/opt/powerautomation")
        self.test_root = self.project_root / "test"
        self.config_path = config_path or self.test_root / "config" / "test_config.yaml"
        
        # 初始化日志
        self._setup_logging()
        
        # 加载配置
        self.config = self._load_config()
        
        # 初始化组件
        self.discovery = TestDiscovery(self.config)
        self.runner = TestRunner(self.config)
        self.reporter = TestReporter(self.config)
        self.scheduler = TestScheduler(self.config, self)
        
        # 测试会话管理
        self.current_session: Optional[TestSession] = None
        self.session_history: List[TestSession] = []
        
        # 状态管理
        self.is_running = False
        self.is_scheduled = False
        
        self.logger.info("TestManager initialized successfully")
    
    def _setup_logging(self):
        """设置日志"""
        log_dir = self.test_root / "logs"
        log_dir.mkdir(exist_ok=True)
        
        # 配置日志格式
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_dir / "test_execution.log"),
                logging.StreamHandler()
            ]
        )
        
        self.logger = logging.getLogger(__name__)
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                self.logger.info(f"Loaded config from {self.config_path}")
                return config
            except Exception as e:
                self.logger.warning(f"Failed to load config: {e}, using defaults")
        
        # 默认配置
        default_config = {
            'test_settings': {
                'parallel_workers': 4,
                'timeout': 300,
                'retry_count': 3,
                'fail_fast': False
            },
            'test_discovery': {
                'include_patterns': [
                    "*/unit_tests/test_*.py",
                    "*/integration_tests/test_*.py"
                ],
                'exclude_patterns': [
                    "*/__pycache__/*",
                    "*/.*",
                    "*/*_backup/*"
                ]
            },
            'reporting': {
                'formats': ['json', 'html'],
                'output_dir': 'reports',
                'include_logs': True,
                'archive_days': 30
            }
        }
        
        # 保存默认配置
        self._save_config(default_config)
        return default_config
    
    def _save_config(self, config: Dict[str, Any]):
        """保存配置"""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
            self.logger.info(f"Saved config to {self.config_path}")
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}")
    
    async def discover_tests(self, 
                           module_filter: Optional[str] = None,
                           test_type_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        发现测试
        
        Args:
            module_filter: 模块过滤器
            test_type_filter: 测试类型过滤器 (unit, integration, comprehensive, simple)
        
        Returns:
            测试列表
        """
        self.logger.info(f"Discovering tests (module: {module_filter}, type: {test_type_filter})")
        
        tests = await self.discovery.discover_tests(
            module_filter=module_filter,
            test_type_filter=test_type_filter
        )
        
        self.logger.info(f"Discovered {len(tests)} tests")
        return tests
    
    async def run_tests(self,
                       tests: Optional[List[Dict[str, Any]]] = None,
                       module_filter: Optional[str] = None,
                       test_type_filter: Optional[str] = None,
                       parallel: bool = True) -> TestSession:
        """
        运行测试
        
        Args:
            tests: 指定的测试列表，如果为None则自动发现
            module_filter: 模块过滤器
            test_type_filter: 测试类型过滤器
            parallel: 是否并行执行
        
        Returns:
            测试会话结果
        """
        if self.is_running:
            raise RuntimeError("Tests are already running")
        
        self.is_running = True
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            # 创建测试会话
            session = TestSession(
                session_id=session_id,
                start_time=datetime.now()
            )
            self.current_session = session
            
            self.logger.info(f"Starting test session: {session_id}")
            
            # 发现测试（如果未提供）
            if tests is None:
                tests = await self.discover_tests(module_filter, test_type_filter)
            
            session.total_tests = len(tests)
            
            if not tests:
                self.logger.warning("No tests found to run")
                session.end_time = datetime.now()
                return session
            
            # 运行测试
            results = await self.runner.run_tests(
                tests=tests,
                parallel=parallel,
                max_workers=self.config['test_settings']['parallel_workers']
            )
            
            # 处理结果
            for result_data in results:
                result = TestResult(
                    test_id=result_data.get('test_id', ''),
                    test_name=result_data.get('test_name', ''),
                    module_name=result_data.get('module_name', ''),
                    test_type=result_data.get('test_type', ''),
                    status=result_data.get('status', 'ERROR'),
                    duration=result_data.get('duration', 0.0),
                    start_time=result_data.get('start_time', session.start_time),
                    end_time=result_data.get('end_time', datetime.now()),
                    error_message=result_data.get('error_message'),
                    details=result_data.get('details')
                )
                
                session.results.append(result)
                
                # 更新统计
                if result.status == 'PASS':
                    session.passed_tests += 1
                elif result.status == 'FAIL':
                    session.failed_tests += 1
                elif result.status == 'ERROR':
                    session.error_tests += 1
                elif result.status == 'SKIP':
                    session.skipped_tests += 1
            
            session.end_time = datetime.now()
            
            # 保存会话历史
            self.session_history.append(session)
            
            # 生成报告
            await self._generate_session_report(session)
            
            self.logger.info(f"Test session completed: {session_id}")
            self.logger.info(f"Results: {session.passed_tests} passed, {session.failed_tests} failed, {session.error_tests} errors, {session.skipped_tests} skipped")
            
            return session
            
        except Exception as e:
            self.logger.error(f"Test session failed: {e}")
            if self.current_session:
                self.current_session.end_time = datetime.now()
            raise
        finally:
            self.is_running = False
            self.current_session = None
    
    async def run_all_tests(self, parallel: bool = True) -> TestSession:
        """运行所有测试"""
        return await self.run_tests(parallel=parallel)
    
    async def run_module_tests(self, module_name: str, parallel: bool = True) -> TestSession:
        """运行指定模块的测试"""
        return await self.run_tests(module_filter=module_name, parallel=parallel)
    
    async def run_smoke_tests(self, parallel: bool = True) -> TestSession:
        """运行冒烟测试（简单测试）"""
        return await self.run_tests(test_type_filter='simple', parallel=parallel)
    
    async def run_comprehensive_tests(self, parallel: bool = True) -> TestSession:
        """运行完整测试"""
        return await self.run_tests(test_type_filter='comprehensive', parallel=parallel)
    
    async def _generate_session_report(self, session: TestSession):
        """生成会话报告"""
        try:
            report_data = {
                'session': asdict(session),
                'summary': {
                    'total': session.total_tests,
                    'passed': session.passed_tests,
                    'failed': session.failed_tests,
                    'errors': session.error_tests,
                    'skipped': session.skipped_tests,
                    'success_rate': session.passed_tests / session.total_tests if session.total_tests > 0 else 0,
                    'duration': (session.end_time - session.start_time).total_seconds() if session.end_time else 0
                }
            }
            
            # 生成报告
            await self.reporter.generate_report(
                report_data=report_data,
                report_type='session',
                session_id=session.session_id
            )
            
        except Exception as e:
            self.logger.error(f"Failed to generate session report: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """获取测试管理器状态"""
        status = {
            'is_running': self.is_running,
            'is_scheduled': self.is_scheduled,
            'current_session': asdict(self.current_session) if self.current_session else None,
            'total_sessions': len(self.session_history),
            'last_session': asdict(self.session_history[-1]) if self.session_history else None,
            'scheduler_status': self.scheduler.get_status() if self.scheduler else None
        }
        
        return status
    
    def get_session_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取会话历史"""
        recent_sessions = self.session_history[-limit:] if limit > 0 else self.session_history
        return [asdict(session) for session in recent_sessions]
    
    def get_test_statistics(self, days: int = 7) -> Dict[str, Any]:
        """获取测试统计信息"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent_sessions = [
            session for session in self.session_history
            if session.start_time >= cutoff_date
        ]
        
        if not recent_sessions:
            return {
                'period_days': days,
                'total_sessions': 0,
                'total_tests': 0,
                'average_success_rate': 0,
                'trend': 'stable'
            }
        
        total_tests = sum(session.total_tests for session in recent_sessions)
        total_passed = sum(session.passed_tests for session in recent_sessions)
        
        # 计算趋势
        if len(recent_sessions) >= 2:
            recent_rate = recent_sessions[-1].passed_tests / recent_sessions[-1].total_tests if recent_sessions[-1].total_tests > 0 else 0
            older_rate = recent_sessions[0].passed_tests / recent_sessions[0].total_tests if recent_sessions[0].total_tests > 0 else 0
            
            if recent_rate > older_rate + 0.05:
                trend = 'improving'
            elif recent_rate < older_rate - 0.05:
                trend = 'declining'
            else:
                trend = 'stable'
        else:
            trend = 'stable'
        
        return {
            'period_days': days,
            'total_sessions': len(recent_sessions),
            'total_tests': total_tests,
            'total_passed': total_passed,
            'average_success_rate': total_passed / total_tests if total_tests > 0 else 0,
            'trend': trend,
            'sessions': [asdict(session) for session in recent_sessions]
        }
    
    async def start_scheduler(self):
        """启动测试调度器"""
        if self.is_scheduled:
            self.logger.warning("Scheduler is already running")
            return
        
        self.logger.info("Starting test scheduler")
        await self.scheduler.start()
        self.is_scheduled = True
    
    async def stop_scheduler(self):
        """停止测试调度器"""
        if not self.is_scheduled:
            self.logger.warning("Scheduler is not running")
            return
        
        self.logger.info("Stopping test scheduler")
        await self.scheduler.stop()
        self.is_scheduled = False
    
    async def cleanup(self):
        """清理资源"""
        self.logger.info("Cleaning up TestManager")
        
        if self.is_scheduled:
            await self.stop_scheduler()
        
        # 清理组件
        if hasattr(self.runner, 'cleanup'):
            await self.runner.cleanup()
        
        if hasattr(self.reporter, 'cleanup'):
            await self.reporter.cleanup()
        
        self.logger.info("TestManager cleanup completed")

# 单例模式
_test_manager_instance = None

def get_test_manager(config_path: Optional[str] = None) -> TestManager:
    """获取测试管理器单例"""
    global _test_manager_instance
    
    if _test_manager_instance is None:
        _test_manager_instance = TestManager(config_path)
    
    return _test_manager_instance

