#!/usr/bin/env python3
"""
PowerAutomation MCP API标准化基类
为所有工作流MCP提供统一的API接口标准实现
"""

from flask import Flask, request, jsonify, g
from flask_cors import CORS
import asyncio
import json
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, List
from functools import wraps
import time

class StandardAPIResponse:
    """标准化API响应类"""
    
    @staticmethod
    def success(data: Any = None, metadata: Optional[Dict] = None) -> Dict:
        """成功响应格式"""
        response = {
            "success": True,
            "data": data,
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "request_id": getattr(g, 'request_id', str(uuid.uuid4())),
                "version": "1.0.0"
            }
        }
        if metadata:
            response["metadata"].update(metadata)
        return response
    
    @staticmethod
    def error(error_code: str, message: str, details: Optional[Dict] = None, 
              status_code: int = 400) -> tuple:
        """错误响应格式"""
        response = {
            "success": False,
            "error": {
                "code": error_code,
                "message": message,
                "details": details or {}
            },
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "request_id": getattr(g, 'request_id', str(uuid.uuid4())),
                "version": "1.0.0"
            }
        }
        return response, status_code
    
    @staticmethod
    def paginated(data: List, page: int, limit: int, total: int, 
                  metadata: Optional[Dict] = None) -> Dict:
        """分页响应格式"""
        total_pages = (total + limit - 1) // limit
        response = {
            "success": True,
            "data": data,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            },
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "request_id": getattr(g, 'request_id', str(uuid.uuid4())),
                "version": "1.0.0"
            }
        }
        if metadata:
            response["metadata"].update(metadata)
        return response

class StandardErrorCodes:
    """标准化错误代码"""
    
    # 通用错误代码
    VALIDATION_ERROR = "VALIDATION_ERROR"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    AUTHORIZATION_ERROR = "AUTHORIZATION_ERROR"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    RESOURCE_CONFLICT = "RESOURCE_CONFLICT"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    
    # 业务特定错误代码
    REQ_ANALYSIS_FAILED = "REQ_ANALYSIS_FAILED"
    ARCH_DESIGN_ERROR = "ARCH_DESIGN_ERROR"
    CODE_GENERATION_FAILED = "CODE_GENERATION_FAILED"
    TEST_EXECUTION_ERROR = "TEST_EXECUTION_ERROR"
    DEPLOYMENT_FAILED = "DEPLOYMENT_FAILED"

class RequestValidator:
    """请求参数验证器"""
    
    @staticmethod
    def validate_required_fields(data: Dict, required_fields: List[str]) -> Optional[tuple]:
        """验证必需字段"""
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return StandardAPIResponse.error(
                StandardErrorCodes.VALIDATION_ERROR,
                f"缺少必需字段: {', '.join(missing_fields)}",
                {"missing_fields": missing_fields}
            )
        return None
    
    @staticmethod
    def validate_pagination_params(page: int, limit: int) -> Optional[tuple]:
        """验证分页参数"""
        if page < 1:
            return StandardAPIResponse.error(
                StandardErrorCodes.VALIDATION_ERROR,
                "页码必须大于0",
                {"field": "page", "value": page}
            )
        if limit < 1 or limit > 100:
            return StandardAPIResponse.error(
                StandardErrorCodes.VALIDATION_ERROR,
                "每页数量必须在1-100之间",
                {"field": "limit", "value": limit}
            )
        return None

def request_id_middleware():
    """请求ID中间件"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            g.request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
            g.start_time = time.time()
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def error_handler(app: Flask):
    """统一错误处理器"""
    
    @app.errorhandler(400)
    def bad_request(error):
        return StandardAPIResponse.error(
            StandardErrorCodes.VALIDATION_ERROR,
            "请求参数错误",
            {"description": str(error)}
        )
    
    @app.errorhandler(401)
    def unauthorized(error):
        return StandardAPIResponse.error(
            StandardErrorCodes.AUTHENTICATION_ERROR,
            "未授权访问",
            {"description": str(error)},
            401
        )
    
    @app.errorhandler(403)
    def forbidden(error):
        return StandardAPIResponse.error(
            StandardErrorCodes.AUTHORIZATION_ERROR,
            "禁止访问",
            {"description": str(error)},
            403
        )
    
    @app.errorhandler(404)
    def not_found(error):
        return StandardAPIResponse.error(
            StandardErrorCodes.RESOURCE_NOT_FOUND,
            "资源不存在",
            {"description": str(error)},
            404
        )
    
    @app.errorhandler(500)
    def internal_error(error):
        return StandardAPIResponse.error(
            StandardErrorCodes.INTERNAL_ERROR,
            "服务器内部错误",
            {"description": str(error)},
            500
        )

class StandardMCPServer:
    """标准化MCP服务器基类"""
    
    def __init__(self, service_name: str, version: str = "1.0.0", port: int = 8080):
        self.service_name = service_name
        self.version = version
        self.port = port
        self.app = Flask(__name__)
        CORS(self.app)
        
        # 配置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(service_name)
        
        # 注册错误处理器
        error_handler(self.app)
        
        # 注册标准端点
        self._register_standard_endpoints()
    
    def _register_standard_endpoints(self):
        """注册标准端点"""
        
        @self.app.route('/api/health', methods=['GET'])
        @request_id_middleware()
        def health_check():
            """基础健康检查"""
            return jsonify({
                "status": "healthy",
                "service": self.service_name,
                "version": self.version,
                "timestamp": datetime.now().isoformat(),
                "uptime": time.time() - getattr(self, 'start_time', time.time())
            })
        
        @self.app.route('/api/health/detailed', methods=['GET'])
        @request_id_middleware()
        def detailed_health_check():
            """详细健康检查"""
            return jsonify({
                "status": "healthy",
                "service": self.service_name,
                "version": self.version,
                "timestamp": datetime.now().isoformat(),
                "uptime": time.time() - getattr(self, 'start_time', time.time()),
                "system_info": self._get_system_info(),
                "performance_metrics": self._get_performance_metrics(),
                "dependencies": self._check_dependencies()
            })
        
        @self.app.route('/api/status', methods=['GET'])
        @request_id_middleware()
        def service_status():
            """服务状态"""
            return jsonify(StandardAPIResponse.success({
                "service_id": self.service_name,
                "version": self.version,
                "status": "active",
                "message": f"{self.service_name}运行正常",
                "capabilities": self._get_capabilities(),
                "endpoints": self._get_endpoints()
            }))
    
    def _get_system_info(self) -> Dict:
        """获取系统信息"""
        import psutil
        return {
            "cpu_usage": f"{psutil.cpu_percent()}%",
            "memory_usage": f"{psutil.virtual_memory().used // 1024 // 1024}MB",
            "disk_usage": f"{psutil.disk_usage('/').used // 1024 // 1024 // 1024}GB"
        }
    
    def _get_performance_metrics(self) -> Dict:
        """获取性能指标"""
        return {
            "requests_per_second": 0,  # 需要实际实现
            "average_response_time": "0ms",  # 需要实际实现
            "error_rate": "0%"  # 需要实际实现
        }
    
    def _check_dependencies(self) -> Dict:
        """检查依赖服务"""
        return {
            "database": "healthy",
            "redis": "healthy",
            "external_api": "healthy"
        }
    
    def _get_capabilities(self) -> List[str]:
        """获取服务能力列表"""
        return []  # 子类需要重写
    
    def _get_endpoints(self) -> List[str]:
        """获取端点列表"""
        return []  # 子类需要重写
    
    def register_endpoint(self, rule: str, methods: List[str] = None):
        """注册端点装饰器"""
        if methods is None:
            methods = ['GET']
        
        def decorator(f):
            @self.app.route(rule, methods=methods)
            @request_id_middleware()
            @wraps(f)
            def wrapper(*args, **kwargs):
                try:
                    # 记录请求开始
                    self.logger.info(f"处理请求: {request.method} {request.path}")
                    
                    # 执行业务逻辑
                    result = f(*args, **kwargs)
                    
                    # 记录请求完成
                    duration = (time.time() - g.start_time) * 1000
                    self.logger.info(f"请求完成: {request.method} {request.path}, 耗时: {duration:.2f}ms")
                    
                    return result
                    
                except Exception as e:
                    # 记录错误
                    self.logger.error(f"请求处理失败: {request.method} {request.path}, 错误: {str(e)}")
                    return StandardAPIResponse.error(
                        StandardErrorCodes.INTERNAL_ERROR,
                        "内部服务错误",
                        {"error_details": str(e)}
                    )
            
            return wrapper
        return decorator
    
    def run(self, host: str = '0.0.0.0', debug: bool = False):
        """启动服务器"""
        self.start_time = time.time()
        self.logger.info(f"启动{self.service_name}...")
        self.logger.info(f"服务地址: http://{host}:{self.port}")
        self.logger.info(f"健康检查: http://{host}:{self.port}/api/health")
        self.logger.info(f"API文档: http://{host}:{self.port}/api/status")
        
        self.app.run(
            host=host,
            port=self.port,
            debug=debug,
            threaded=True
        )

# 使用示例：Requirements Analysis MCP Server的标准化实现
class RequirementsAnalysisMCPServer(StandardMCPServer):
    """需求分析MCP服务器标准化实现"""
    
    def __init__(self):
        super().__init__("Requirements Analysis MCP", "1.0.0", 8091)
        self._register_business_endpoints()
    
    def _get_capabilities(self) -> List[str]:
        """获取服务能力列表"""
        return [
            "需求收集和分析",
            "用户故事生成",
            "功能规格定义",
            "验收标准制定"
        ]
    
    def _get_endpoints(self) -> List[str]:
        """获取端点列表"""
        return [
            "/api/status",
            "/api/health",
            "/api/analyze_requirements",
            "/api/generate_user_stories",
            "/api/define_specifications",
            "/api/create_acceptance_criteria"
        ]
    
    def _register_business_endpoints(self):
        """注册业务端点"""
        
        @self.register_endpoint('/api/analyze_requirements', ['POST'])
        def analyze_requirements():
            """分析需求"""
            data = request.get_json()
            if not data:
                return StandardAPIResponse.error(
                    StandardErrorCodes.VALIDATION_ERROR,
                    "缺少请求数据"
                )
            
            # 验证必需字段
            validation_error = RequestValidator.validate_required_fields(
                data, ['requirements']
            )
            if validation_error:
                return validation_error
            
            # 业务逻辑处理
            result = self._process_requirements_analysis(data)
            
            return jsonify(StandardAPIResponse.success(result))
        
        @self.register_endpoint('/api/generate_user_stories', ['POST'])
        def generate_user_stories():
            """生成用户故事"""
            data = request.get_json()
            if not data:
                return StandardAPIResponse.error(
                    StandardErrorCodes.VALIDATION_ERROR,
                    "缺少请求数据"
                )
            
            # 业务逻辑处理
            result = self._process_user_stories_generation(data)
            
            return jsonify(StandardAPIResponse.success(result))
    
    def _process_requirements_analysis(self, data: Dict) -> Dict:
        """处理需求分析业务逻辑"""
        # 这里实现具体的需求分析逻辑
        return {
            "analysis": {
                "functional_requirements": ["用户注册和登录功能"],
                "non_functional_requirements": ["性能要求：响应时间<2秒"],
                "constraints": ["预算限制"],
                "assumptions": ["用户具备基本计算机操作能力"]
            },
            "confidence_score": 0.85
        }
    
    def _process_user_stories_generation(self, data: Dict) -> Dict:
        """处理用户故事生成业务逻辑"""
        # 这里实现具体的用户故事生成逻辑
        return {
            "user_stories": [
                {
                    "id": "US001",
                    "title": "用户注册",
                    "description": "作为一个新用户，我希望能够注册账户，以便使用系统功能",
                    "acceptance_criteria": ["用户可以输入邮箱和密码"],
                    "priority": "高",
                    "story_points": 5
                }
            ],
            "total_story_points": 5,
            "estimated_sprints": 1
        }

if __name__ == '__main__':
    # 启动标准化的Requirements Analysis MCP服务器
    server = RequirementsAnalysisMCPServer()
    server.run()

