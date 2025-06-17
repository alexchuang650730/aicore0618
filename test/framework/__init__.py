"""
PowerAutomation 统一测试框架
中央化测试管理系统
"""

from .test_manager import TestManager
from .test_scheduler import TestScheduler
from .test_runner import TestRunner
from .test_reporter import TestReporter
from .test_discovery import TestDiscovery

__version__ = "1.3.0"
__author__ = "PowerAutomation Team"

__all__ = [
    'TestManager',
    'TestScheduler', 
    'TestRunner',
    'TestReporter',
    'TestDiscovery'
]

