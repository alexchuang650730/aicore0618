"""
错误处理工具集
Error Handling Utilities for PowerAutomation
"""

from .enhanced_error_handler import (
    EnhancedErrorHandler,
    ErrorSeverity,
    ErrorCategory,
    RecoveryStrategy,
    ErrorContext,
    RecoveryAction,
    get_error_handler,
    error_handler_decorator
)

__all__ = [
    'EnhancedErrorHandler',
    'ErrorSeverity',
    'ErrorCategory', 
    'RecoveryStrategy',
    'ErrorContext',
    'RecoveryAction',
    'get_error_handler',
    'error_handler_decorator'
]

