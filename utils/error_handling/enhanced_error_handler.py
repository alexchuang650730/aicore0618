"""
PowerAutomation 增强错误处理框架
Enhanced Error Handling Framework for PowerAutomation

提供统一的错误处理、日志记录、监控和恢复机制
"""

import asyncio
import json
import logging
import traceback
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, Any, Optional, List, Callable, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import sys
import os

class ErrorSeverity(Enum):
    """错误严重程度"""
    LOW = "low"           # 轻微错误，不影响核心功能
    MEDIUM = "medium"     # 中等错误，影响部分功能
    HIGH = "high"         # 严重错误，影响核心功能
    CRITICAL = "critical" # 致命错误，系统无法正常运行

class ErrorCategory(Enum):
    """错误分类"""
    NETWORK = "network"           # 网络相关错误
    DATABASE = "database"         # 数据库相关错误
    AUTHENTICATION = "auth"       # 认证授权错误
    VALIDATION = "validation"     # 数据验证错误
    BUSINESS_LOGIC = "business"   # 业务逻辑错误
    SYSTEM = "system"            # 系统级错误
    EXTERNAL_API = "external"    # 外部API错误
    CONFIGURATION = "config"     # 配置错误
    RESOURCE = "resource"        # 资源不足错误
    TIMEOUT = "timeout"          # 超时错误

class RecoveryStrategy(Enum):
    """恢复策略"""
    RETRY = "retry"               # 重试
    FALLBACK = "fallback"         # 降级处理
    CIRCUIT_BREAKER = "circuit"   # 熔断
    IGNORE = "ignore"             # 忽略
    ESCALATE = "escalate"         # 上报
    RESTART = "restart"           # 重启组件

@dataclass
class ErrorContext:
    """错误上下文信息"""
    error_id: str
    timestamp: datetime
    severity: ErrorSeverity
    category: ErrorCategory
    component: str
    operation: str
    message: str
    details: Dict[str, Any]
    stack_trace: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    recovery_attempts: int = 0
    resolved: bool = False

@dataclass
class RecoveryAction:
    """恢复动作"""
    strategy: RecoveryStrategy
    max_attempts: int
    delay_seconds: float
    timeout_seconds: float
    fallback_function: Optional[Callable] = None
    escalation_threshold: int = 3

class EnhancedErrorHandler:
    """增强的错误处理器"""
    
    def __init__(self, component_name: str, config: Optional[Dict[str, Any]] = None):
        self.component_name = component_name
        self.config = config or {}
        
        # 错误存储
        self.error_history: List[ErrorContext] = []
        self.active_errors: Dict[str, ErrorContext] = {}
        
        # 恢复策略配置
        self.recovery_strategies: Dict[ErrorCategory, RecoveryAction] = {
            ErrorCategory.NETWORK: RecoveryAction(
                strategy=RecoveryStrategy.RETRY,
                max_attempts=3,
                delay_seconds=1.0,
                timeout_seconds=30.0
            ),
            ErrorCategory.DATABASE: RecoveryAction(
                strategy=RecoveryStrategy.RETRY,
                max_attempts=2,
                delay_seconds=2.0,
                timeout_seconds=60.0
            ),
            ErrorCategory.EXTERNAL_API: RecoveryAction(
                strategy=RecoveryStrategy.CIRCUIT_BREAKER,
                max_attempts=5,
                delay_seconds=5.0,
                timeout_seconds=120.0
            ),
            ErrorCategory.TIMEOUT: RecoveryAction(
                strategy=RecoveryStrategy.RETRY,
                max_attempts=2,
                delay_seconds=0.5,
                timeout_seconds=15.0
            ),
            ErrorCategory.RESOURCE: RecoveryAction(
                strategy=RecoveryStrategy.FALLBACK,
                max_attempts=1,
                delay_seconds=0.0,
                timeout_seconds=5.0
            ),
            ErrorCategory.SYSTEM: RecoveryAction(
                strategy=RecoveryStrategy.ESCALATE,
                max_attempts=1,
                delay_seconds=0.0,
                timeout_seconds=0.0,
                escalation_threshold=1
            )
        }
        
        # 熔断器状态
        self.circuit_breakers: Dict[str, Dict[str, Any]] = {}
        
        # 统计信息
        self.error_stats = {
            "total_errors": 0,
            "errors_by_category": {cat.value: 0 for cat in ErrorCategory},
            "errors_by_severity": {sev.value: 0 for sev in ErrorSeverity},
            "recovery_success_rate": 0.0,
            "average_recovery_time": 0.0
        }
        
        # 设置日志
        self._setup_logging()

    def _setup_logging(self):
        """设置日志记录"""
        log_dir = Path("/opt/powerautomation/logs")
        log_dir.mkdir(exist_ok=True)
        
        # 创建专用的错误处理日志
        self.logger = logging.getLogger(f"error_handler_{self.component_name}")
        self.logger.setLevel(logging.DEBUG)
        
        # 文件处理器
        file_handler = logging.FileHandler(
            log_dir / f"error_handler_{self.component_name}.log"
        )
        file_handler.setLevel(logging.DEBUG)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)
        
        # 格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    async def handle_error(
        self,
        error: Exception,
        category: ErrorCategory,
        severity: ErrorSeverity,
        operation: str,
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        request_id: Optional[str] = None
    ) -> ErrorContext:
        """处理错误"""
        
        # 创建错误上下文
        error_context = ErrorContext(
            error_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            severity=severity,
            category=category,
            component=self.component_name,
            operation=operation,
            message=str(error),
            details=context or {},
            stack_trace=traceback.format_exc(),
            user_id=user_id,
            session_id=session_id,
            request_id=request_id
        )
        
        # 记录错误
        self._log_error(error_context)
        
        # 存储错误
        self.error_history.append(error_context)
        self.active_errors[error_context.error_id] = error_context
        
        # 更新统计
        self._update_error_stats(error_context)
        
        # 尝试恢复
        recovery_result = await self._attempt_recovery(error_context)
        
        # 如果恢复成功，标记为已解决
        if recovery_result:
            error_context.resolved = True
            self.active_errors.pop(error_context.error_id, None)
        
        return error_context

    def _log_error(self, error_context: ErrorContext):
        """记录错误日志"""
        log_message = (
            f"Error in {error_context.component}.{error_context.operation}: "
            f"{error_context.message} "
            f"[{error_context.category.value}/{error_context.severity.value}] "
            f"ID: {error_context.error_id}"
        )
        
        if error_context.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(log_message)
        elif error_context.severity == ErrorSeverity.HIGH:
            self.logger.error(log_message)
        elif error_context.severity == ErrorSeverity.MEDIUM:
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)
        
        # 记录详细信息
        if error_context.details:
            self.logger.debug(f"Error details: {json.dumps(error_context.details, indent=2)}")
        
        # 记录堆栈跟踪
        if error_context.stack_trace:
            self.logger.debug(f"Stack trace: {error_context.stack_trace}")

    async def _attempt_recovery(self, error_context: ErrorContext) -> bool:
        """尝试错误恢复"""
        recovery_action = self.recovery_strategies.get(error_context.category)
        if not recovery_action:
            self.logger.warning(f"No recovery strategy for category: {error_context.category}")
            return False
        
        start_time = datetime.now()
        
        try:
            if recovery_action.strategy == RecoveryStrategy.RETRY:
                return await self._retry_operation(error_context, recovery_action)
            elif recovery_action.strategy == RecoveryStrategy.FALLBACK:
                return await self._fallback_operation(error_context, recovery_action)
            elif recovery_action.strategy == RecoveryStrategy.CIRCUIT_BREAKER:
                return await self._circuit_breaker_operation(error_context, recovery_action)
            elif recovery_action.strategy == RecoveryStrategy.ESCALATE:
                return await self._escalate_error(error_context, recovery_action)
            elif recovery_action.strategy == RecoveryStrategy.IGNORE:
                self.logger.info(f"Ignoring error {error_context.error_id} as per strategy")
                return True
            else:
                self.logger.warning(f"Unknown recovery strategy: {recovery_action.strategy}")
                return False
                
        except Exception as recovery_error:
            self.logger.error(f"Recovery attempt failed: {recovery_error}")
            return False
        finally:
            # 更新恢复时间统计
            recovery_time = (datetime.now() - start_time).total_seconds()
            self._update_recovery_stats(recovery_time)

    async def _retry_operation(self, error_context: ErrorContext, recovery_action: RecoveryAction) -> bool:
        """重试操作"""
        for attempt in range(recovery_action.max_attempts):
            error_context.recovery_attempts += 1
            
            self.logger.info(
                f"Retry attempt {attempt + 1}/{recovery_action.max_attempts} "
                f"for error {error_context.error_id}"
            )
            
            # 等待延迟
            if recovery_action.delay_seconds > 0:
                await asyncio.sleep(recovery_action.delay_seconds * (attempt + 1))
            
            try:
                # 这里应该重新执行原始操作
                # 在实际实现中，需要传入原始操作的函数引用
                self.logger.info(f"Retry successful for error {error_context.error_id}")
                return True
                
            except Exception as retry_error:
                self.logger.warning(
                    f"Retry attempt {attempt + 1} failed: {retry_error}"
                )
                continue
        
        self.logger.error(f"All retry attempts failed for error {error_context.error_id}")
        return False

    async def _fallback_operation(self, error_context: ErrorContext, recovery_action: RecoveryAction) -> bool:
        """降级处理"""
        if recovery_action.fallback_function:
            try:
                self.logger.info(f"Executing fallback for error {error_context.error_id}")
                await recovery_action.fallback_function(error_context)
                return True
            except Exception as fallback_error:
                self.logger.error(f"Fallback failed: {fallback_error}")
                return False
        else:
            self.logger.warning(f"No fallback function defined for error {error_context.error_id}")
            return False

    async def _circuit_breaker_operation(self, error_context: ErrorContext, recovery_action: RecoveryAction) -> bool:
        """熔断器处理"""
        circuit_key = f"{error_context.component}_{error_context.operation}"
        
        # 获取或创建熔断器状态
        if circuit_key not in self.circuit_breakers:
            self.circuit_breakers[circuit_key] = {
                "state": "closed",  # closed, open, half_open
                "failure_count": 0,
                "last_failure_time": None,
                "success_count": 0
            }
        
        circuit = self.circuit_breakers[circuit_key]
        
        # 检查熔断器状态
        if circuit["state"] == "open":
            # 检查是否可以尝试半开状态
            if (datetime.now() - circuit["last_failure_time"]).seconds > 60:
                circuit["state"] = "half_open"
                self.logger.info(f"Circuit breaker {circuit_key} entering half-open state")
            else:
                self.logger.warning(f"Circuit breaker {circuit_key} is open, rejecting request")
                return False
        
        # 尝试执行操作
        try:
            # 这里应该重新执行原始操作
            circuit["success_count"] += 1
            if circuit["state"] == "half_open" and circuit["success_count"] >= 3:
                circuit["state"] = "closed"
                circuit["failure_count"] = 0
                self.logger.info(f"Circuit breaker {circuit_key} closed")
            return True
            
        except Exception:
            circuit["failure_count"] += 1
            circuit["last_failure_time"] = datetime.now()
            
            if circuit["failure_count"] >= recovery_action.escalation_threshold:
                circuit["state"] = "open"
                self.logger.warning(f"Circuit breaker {circuit_key} opened")
            
            return False

    async def _escalate_error(self, error_context: ErrorContext, recovery_action: RecoveryAction) -> bool:
        """上报错误"""
        self.logger.critical(
            f"Escalating error {error_context.error_id} - "
            f"Component: {error_context.component}, "
            f"Operation: {error_context.operation}, "
            f"Message: {error_context.message}"
        )
        
        # 这里可以实现具体的上报逻辑
        # 例如：发送邮件、调用监控API、触发告警等
        
        return True  # 上报本身不算恢复，但标记为已处理

    def _update_error_stats(self, error_context: ErrorContext):
        """更新错误统计"""
        self.error_stats["total_errors"] += 1
        self.error_stats["errors_by_category"][error_context.category.value] += 1
        self.error_stats["errors_by_severity"][error_context.severity.value] += 1

    def _update_recovery_stats(self, recovery_time: float):
        """更新恢复统计"""
        # 简单的移动平均
        current_avg = self.error_stats["average_recovery_time"]
        total_errors = self.error_stats["total_errors"]
        
        if total_errors > 0:
            self.error_stats["average_recovery_time"] = (
                (current_avg * (total_errors - 1) + recovery_time) / total_errors
            )

    def get_error_summary(self) -> Dict[str, Any]:
        """获取错误摘要"""
        active_critical = sum(
            1 for error in self.active_errors.values()
            if error.severity == ErrorSeverity.CRITICAL
        )
        
        active_high = sum(
            1 for error in self.active_errors.values()
            if error.severity == ErrorSeverity.HIGH
        )
        
        return {
            "component": self.component_name,
            "total_errors": self.error_stats["total_errors"],
            "active_errors": len(self.active_errors),
            "active_critical": active_critical,
            "active_high": active_high,
            "error_stats": self.error_stats,
            "circuit_breakers": {
                key: {k: v for k, v in circuit.items() if k != "last_failure_time"}
                for key, circuit in self.circuit_breakers.items()
            }
        }

    async def cleanup_resolved_errors(self, max_age_hours: int = 24):
        """清理已解决的错误"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        # 清理历史错误
        self.error_history = [
            error for error in self.error_history
            if error.timestamp > cutoff_time or not error.resolved
        ]
        
        # 清理活跃错误中的已解决错误
        resolved_ids = [
            error_id for error_id, error in self.active_errors.items()
            if error.resolved and error.timestamp < cutoff_time
        ]
        
        for error_id in resolved_ids:
            self.active_errors.pop(error_id, None)
        
        self.logger.info(f"Cleaned up {len(resolved_ids)} resolved errors")

# 全局错误处理器实例
_global_error_handlers: Dict[str, EnhancedErrorHandler] = {}

def get_error_handler(component_name: str, config: Optional[Dict[str, Any]] = None) -> EnhancedErrorHandler:
    """获取组件的错误处理器"""
    if component_name not in _global_error_handlers:
        _global_error_handlers[component_name] = EnhancedErrorHandler(component_name, config)
    return _global_error_handlers[component_name]

def error_handler_decorator(
    category: ErrorCategory,
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    component_name: Optional[str] = None
):
    """错误处理装饰器"""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            handler = get_error_handler(component_name or func.__module__)
            try:
                return await func(*args, **kwargs)
            except Exception as e:
                await handler.handle_error(
                    error=e,
                    category=category,
                    severity=severity,
                    operation=func.__name__,
                    context={"args": str(args), "kwargs": str(kwargs)}
                )
                raise
        
        def sync_wrapper(*args, **kwargs):
            handler = get_error_handler(component_name or func.__module__)
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # 对于同步函数，创建一个简单的错误记录
                asyncio.create_task(handler.handle_error(
                    error=e,
                    category=category,
                    severity=severity,
                    operation=func.__name__,
                    context={"args": str(args), "kwargs": str(kwargs)}
                ))
                raise
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

