#!/usr/bin/env python3
"""
PowerAutomation 测试调度器
负责定期测试和任务调度
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
import yaml
import threading
import time
from pathlib import Path

# 简化的cron解析器
class CronParser:
    """简化的cron表达式解析器"""
    
    @staticmethod
    def parse_cron(cron_expr: str) -> Dict[str, Any]:
        """
        解析cron表达式
        格式: "分 时 日 月 周"
        """
        parts = cron_expr.strip().split()
        if len(parts) != 5:
            raise ValueError(f"Invalid cron expression: {cron_expr}")
        
        return {
            'minute': parts[0],
            'hour': parts[1], 
            'day': parts[2],
            'month': parts[3],
            'weekday': parts[4]
        }
    
    @staticmethod
    def should_run(cron_expr: str, current_time: datetime) -> bool:
        """检查是否应该在当前时间运行"""
        try:
            cron = CronParser.parse_cron(cron_expr)
            
            # 简化的匹配逻辑
            def matches(value: str, current: int, max_val: int) -> bool:
                if value == '*':
                    return True
                if '/' in value:
                    step = int(value.split('/')[1])
                    return current % step == 0
                if ',' in value:
                    return str(current) in value.split(',')
                return str(current) == value
            
            return (
                matches(cron['minute'], current_time.minute, 59) and
                matches(cron['hour'], current_time.hour, 23) and
                matches(cron['day'], current_time.day, 31) and
                matches(cron['month'], current_time.month, 12) and
                matches(cron['weekday'], current_time.weekday(), 6)
            )
            
        except Exception as e:
            logging.error(f"Error parsing cron expression {cron_expr}: {e}")
            return False

@dataclass
class ScheduledTask:
    """调度任务"""
    task_id: str
    name: str
    cron_expr: str
    test_filter: Dict[str, Any]
    enabled: bool = True
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    run_count: int = 0

class TestScheduler:
    """
    PowerAutomation 测试调度器
    
    功能:
    - 定期测试调度
    - cron表达式支持
    - 任务管理
    - 调度状态监控
    """
    
    def __init__(self, config: Dict[str, Any], test_manager):
        self.config = config
        self.test_manager = test_manager
        self.project_root = Path("/opt/powerautomation")
        self.schedule_config_path = self.project_root / "test" / "config" / "schedule_config.yaml"
        
        # 设置日志
        self.logger = logging.getLogger(__name__)
        
        # 调度状态
        self.is_running = False
        self.scheduler_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        
        # 任务管理
        self.scheduled_tasks: Dict[str, ScheduledTask] = {}
        
        # 加载调度配置
        self._load_schedule_config()
        
        self.logger.info("TestScheduler initialized")
    
    def _load_schedule_config(self):
        """加载调度配置"""
        if self.schedule_config_path.exists():
            try:
                with open(self.schedule_config_path, 'r', encoding='utf-8') as f:
                    schedule_config = yaml.safe_load(f)
                self._parse_schedule_config(schedule_config)
                self.logger.info(f"Loaded schedule config from {self.schedule_config_path}")
                return
            except Exception as e:
                self.logger.warning(f"Failed to load schedule config: {e}")
        
        # 创建默认调度配置
        default_config = {
            'schedules': {
                'daily_comprehensive_test': {
                    'cron': '0 2 * * *',  # 每天凌晨2点
                    'description': '每日完整测试',
                    'test_filter': {
                        'test_type': 'comprehensive'
                    },
                    'enabled': True
                },
                'hourly_smoke_test': {
                    'cron': '0 * * * *',  # 每小时
                    'description': '每小时冒烟测试',
                    'test_filter': {
                        'test_type': 'simple'
                    },
                    'enabled': False  # 默认关闭，避免过于频繁
                },
                'weekly_full_test': {
                    'cron': '0 3 * * 0',  # 每周日凌晨3点
                    'description': '每周完整测试',
                    'test_filter': {},  # 所有测试
                    'enabled': True
                }
            }
        }
        
        self._save_schedule_config(default_config)
        self._parse_schedule_config(default_config)
    
    def _save_schedule_config(self, config: Dict[str, Any]):
        """保存调度配置"""
        try:
            self.schedule_config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.schedule_config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
            self.logger.info(f"Saved schedule config to {self.schedule_config_path}")
        except Exception as e:
            self.logger.error(f"Failed to save schedule config: {e}")
    
    def _parse_schedule_config(self, config: Dict[str, Any]):
        """解析调度配置"""
        schedules = config.get('schedules', {})
        
        for task_id, task_config in schedules.items():
            task = ScheduledTask(
                task_id=task_id,
                name=task_config.get('description', task_id),
                cron_expr=task_config.get('cron', '0 0 * * *'),
                test_filter=task_config.get('test_filter', {}),
                enabled=task_config.get('enabled', True)
            )
            
            self.scheduled_tasks[task_id] = task
            self.logger.info(f"Loaded scheduled task: {task_id} ({task.cron_expr})")
    
    async def start(self):
        """启动调度器"""
        if self.is_running:
            self.logger.warning("Scheduler is already running")
            return
        
        self.is_running = True
        self.stop_event.clear()
        
        # 启动调度线程
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        
        self.logger.info("Test scheduler started")
    
    async def stop(self):
        """停止调度器"""
        if not self.is_running:
            self.logger.warning("Scheduler is not running")
            return
        
        self.is_running = False
        self.stop_event.set()
        
        # 等待调度线程结束
        if self.scheduler_thread and self.scheduler_thread.is_alive():
            self.scheduler_thread.join(timeout=5)
        
        self.logger.info("Test scheduler stopped")
    
    def _scheduler_loop(self):
        """调度器主循环"""
        self.logger.info("Scheduler loop started")
        
        while not self.stop_event.is_set():
            try:
                current_time = datetime.now()
                
                # 检查每个任务
                for task in self.scheduled_tasks.values():
                    if not task.enabled:
                        continue
                    
                    # 检查是否应该运行
                    if self._should_run_task(task, current_time):
                        self.logger.info(f"Triggering scheduled task: {task.task_id}")
                        
                        # 异步运行任务
                        asyncio.run_coroutine_threadsafe(
                            self._run_scheduled_task(task),
                            asyncio.get_event_loop()
                        )
                        
                        # 更新任务状态
                        task.last_run = current_time
                        task.run_count += 1
                
                # 等待1分钟再检查
                self.stop_event.wait(60)
                
            except Exception as e:
                self.logger.error(f"Error in scheduler loop: {e}")
                self.stop_event.wait(60)  # 出错后等待1分钟再继续
        
        self.logger.info("Scheduler loop ended")
    
    def _should_run_task(self, task: ScheduledTask, current_time: datetime) -> bool:
        """检查任务是否应该运行"""
        # 检查cron表达式
        if not CronParser.should_run(task.cron_expr, current_time):
            return False
        
        # 检查是否在同一分钟内已经运行过
        if task.last_run and task.last_run.replace(second=0, microsecond=0) == current_time.replace(second=0, microsecond=0):
            return False
        
        return True
    
    async def _run_scheduled_task(self, task: ScheduledTask):
        """运行调度任务"""
        try:
            self.logger.info(f"Running scheduled task: {task.name}")
            
            # 构建测试过滤器
            module_filter = task.test_filter.get('module')
            test_type_filter = task.test_filter.get('test_type')
            
            # 运行测试
            session = await self.test_manager.run_tests(
                module_filter=module_filter,
                test_type_filter=test_type_filter,
                parallel=True
            )
            
            self.logger.info(f"Scheduled task completed: {task.name}")
            self.logger.info(f"Results: {session.passed_tests}/{session.total_tests} passed")
            
        except Exception as e:
            self.logger.error(f"Scheduled task failed: {task.name}, error: {e}")
    
    def add_task(self, 
                 task_id: str,
                 name: str,
                 cron_expr: str,
                 test_filter: Dict[str, Any],
                 enabled: bool = True) -> bool:
        """添加调度任务"""
        try:
            # 验证cron表达式
            CronParser.parse_cron(cron_expr)
            
            task = ScheduledTask(
                task_id=task_id,
                name=name,
                cron_expr=cron_expr,
                test_filter=test_filter,
                enabled=enabled
            )
            
            self.scheduled_tasks[task_id] = task
            self.logger.info(f"Added scheduled task: {task_id}")
            
            # 保存配置
            self._save_current_config()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add task {task_id}: {e}")
            return False
    
    def remove_task(self, task_id: str) -> bool:
        """移除调度任务"""
        if task_id in self.scheduled_tasks:
            del self.scheduled_tasks[task_id]
            self.logger.info(f"Removed scheduled task: {task_id}")
            
            # 保存配置
            self._save_current_config()
            
            return True
        else:
            self.logger.warning(f"Task not found: {task_id}")
            return False
    
    def enable_task(self, task_id: str) -> bool:
        """启用任务"""
        if task_id in self.scheduled_tasks:
            self.scheduled_tasks[task_id].enabled = True
            self.logger.info(f"Enabled task: {task_id}")
            self._save_current_config()
            return True
        return False
    
    def disable_task(self, task_id: str) -> bool:
        """禁用任务"""
        if task_id in self.scheduled_tasks:
            self.scheduled_tasks[task_id].enabled = False
            self.logger.info(f"Disabled task: {task_id}")
            self._save_current_config()
            return True
        return False
    
    def _save_current_config(self):
        """保存当前配置"""
        config = {
            'schedules': {}
        }
        
        for task_id, task in self.scheduled_tasks.items():
            config['schedules'][task_id] = {
                'cron': task.cron_expr,
                'description': task.name,
                'test_filter': task.test_filter,
                'enabled': task.enabled
            }
        
        self._save_schedule_config(config)
    
    def get_status(self) -> Dict[str, Any]:
        """获取调度器状态"""
        tasks_status = []
        
        for task in self.scheduled_tasks.values():
            tasks_status.append({
                'task_id': task.task_id,
                'name': task.name,
                'cron_expr': task.cron_expr,
                'enabled': task.enabled,
                'last_run': task.last_run.isoformat() if task.last_run else None,
                'run_count': task.run_count,
                'test_filter': task.test_filter
            })
        
        return {
            'is_running': self.is_running,
            'total_tasks': len(self.scheduled_tasks),
            'enabled_tasks': sum(1 for task in self.scheduled_tasks.values() if task.enabled),
            'tasks': tasks_status
        }
    
    def get_next_runs(self, hours: int = 24) -> List[Dict[str, Any]]:
        """获取未来指定小时内的运行计划"""
        current_time = datetime.now()
        end_time = current_time + timedelta(hours=hours)
        
        next_runs = []
        
        # 检查每分钟
        check_time = current_time.replace(second=0, microsecond=0)
        while check_time <= end_time:
            for task in self.scheduled_tasks.values():
                if task.enabled and CronParser.should_run(task.cron_expr, check_time):
                    next_runs.append({
                        'task_id': task.task_id,
                        'name': task.name,
                        'scheduled_time': check_time.isoformat(),
                        'test_filter': task.test_filter
                    })
            
            check_time += timedelta(minutes=1)
        
        return sorted(next_runs, key=lambda x: x['scheduled_time'])

