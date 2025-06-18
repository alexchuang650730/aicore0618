#!/usr/bin/env python3
"""
Test Manager MCP - 测试管理器工作流
基于现有的PowerAutomation测试框架，提供统一的测试管理和执行能力
运行在8097端口
"""

import asyncio
import json
import sys
import os
from pathlib import Path
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import logging
from typing import Dict, List, Any, Optional

# 添加测试框架路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "test"))

try:
    from framework.test_manager import get_test_manager, TestManager
    from framework.test_discovery import TestDiscovery
    from framework.test_runner import TestRunner
    from framework.test_reporter import TestReporter
except ImportError as e:
    logging.error(f"无法导入测试框架: {e}")
    # 创建简化的测试管理器
    class TestManager:
        def __init__(self):
            self.logger = logging.getLogger(__name__)
        
        async def discover_tests(self, **kwargs):
            return []
        
        async def run_tests(self, **kwargs):
            return {"status": "error", "message": "测试框架未正确安装"}

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

class TestManagerMCP:
    """测试管理器MCP - 包装现有的测试框架"""
    
    def __init__(self):
        self.service_id = "test_manager_mcp"
        self.version = "1.0.0"
        self.status = "running"
        
        # 初始化测试管理器
        try:
            self.test_manager = get_test_manager()
            logger.info("✅ 成功连接到PowerAutomation测试框架")
        except Exception as e:
            logger.error(f"❌ 测试框架初始化失败: {e}")
            self.test_manager = TestManager()  # 使用简化版本
        
        # 测试类型映射
        self.test_type_mapping = {
            "unit": "unit",
            "integration": "integration", 
            "comprehensive": "comprehensive",
            "smoke": "simple",
            "all": None
        }
        
        logger.info(f"✅ Test Manager MCP 初始化完成")
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """处理测试管理请求"""
        request_type = data.get("type")
        
        try:
            if request_type == "discover_tests":
                result = await self.discover_tests_by_project(data.get('project_info', {}))
                return {"success": True, "results": result}
            elif request_type == "execute_tests":
                result = await self.execute_test_plan(
                    data.get('test_plan', {}),
                    data.get('project_info', {})
                )
                return {"success": True, "results": result}
            else:
                return {
                    "success": False,
                    "error": f"未知请求类型: {request_type}"
                }
                
        except Exception as e:
            logger.error(f"处理请求失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "request_type": request_type
            }
    
    async def discover_tests_by_project(self, project_info: Dict[str, Any]) -> Dict[str, Any]:
        """根据项目信息发现测试"""
        try:
            project_path = project_info.get('path', '.')
            test_types = project_info.get('test_types', ['unit', 'integration'])
            
            discovered_tests = {}
            
            for test_type in test_types:
                mapped_type = self.test_type_mapping.get(test_type, test_type)
                tests = await self.test_manager.discover_tests(
                    path=project_path,
                    test_type=mapped_type
                )
                discovered_tests[test_type] = tests
            
            return {
                "project_path": project_path,
                "discovered_tests": discovered_tests,
                "total_tests": sum(len(tests) for tests in discovered_tests.values()),
                "test_types": test_types
            }
            
        except Exception as e:
            logger.error(f"测试发现失败: {e}")
            return {
                "error": str(e),
                "project_path": project_info.get('path', ''),
                "discovered_tests": {},
                "total_tests": 0
            }
    
    async def execute_test_plan(self, test_plan: Dict[str, Any], project_info: Dict[str, Any]) -> Dict[str, Any]:
        """执行测试计划"""
        try:
            test_type = test_plan.get('type', 'comprehensive')
            test_files = test_plan.get('test_files', [])
            config = test_plan.get('config', {})
            
            # 执行测试
            execution_result = await self.test_manager.run_tests(
                test_type=self.test_type_mapping.get(test_type, test_type),
                test_files=test_files,
                **config
            )
            
            return {
                "execution_id": f"exec_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "test_plan": test_plan,
                "execution_result": execution_result,
                "status": "completed",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"测试执行失败: {e}")
            return {
                "execution_id": f"exec_failed_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "test_plan": test_plan,
                "error": str(e),
                "status": "failed",
                "timestamp": datetime.now().isoformat()
            }

# 创建测试管理器实例
test_manager_mcp = TestManagerMCP()

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        "service": test_manager_mcp.service_id,
        "version": test_manager_mcp.version,
        "status": test_manager_mcp.status,
        "timestamp": datetime.now().isoformat(),
        "capabilities": [
            "测试发现",
            "测试执行",
            "测试报告",
            "测试管理"
        ]
    })

@app.route('/api/status', methods=['GET'])
def service_status():
    """服务状态"""
    return jsonify({
        "success": True,
        "service_id": test_manager_mcp.service_id,
        "version": test_manager_mcp.version,
        "status": test_manager_mcp.status,
        "message": "Test Manager MCP运行正常",
        "capabilities": [
            "测试发现",
            "测试执行",
            "测试报告",
            "测试管理"
        ],
        "endpoints": [
            "/api/status",
            "/api/health",
            "/api/discover_tests",
            "/api/execute_tests",
            "/api/test_report",
            "/api/test_status"
        ],
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/discover_tests', methods=['POST'])
def discover_tests():
    """发现测试"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "缺少请求数据"}), 400
        
        # 异步处理
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(test_manager_mcp.process({
            'type': 'discover_tests',
            'project_info': data.get('project_info', {})
        }))
        loop.close()
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"测试发现失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/execute_tests', methods=['POST'])
def execute_tests():
    """执行测试"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "缺少请求数据"}), 400
        
        # 异步处理
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(test_manager_mcp.process({
            'type': 'execute_tests',
            'test_plan': data.get('test_plan', {}),
            'project_info': data.get('project_info', {})
        }))
        loop.close()
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"测试执行失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/test_report', methods=['GET'])
def get_test_report():
    """获取测试报告"""
    try:
        execution_id = request.args.get('execution_id')
        
        # 模拟测试报告
        report = {
            "success": True,
            "execution_id": execution_id,
            "report": {
                "summary": {
                    "total_tests": 25,
                    "passed_tests": 22,
                    "failed_tests": 2,
                    "skipped_tests": 1,
                    "success_rate": 88.0,
                    "execution_time": "2.5s"
                },
                "test_results": [
                    {
                        "test_name": "test_user_authentication",
                        "status": "passed",
                        "duration": "0.15s",
                        "message": "测试通过"
                    },
                    {
                        "test_name": "test_data_validation",
                        "status": "failed",
                        "duration": "0.08s",
                        "message": "断言失败: 期望值不匹配"
                    }
                ],
                "coverage": {
                    "line_coverage": 85.2,
                    "branch_coverage": 78.5,
                    "function_coverage": 92.1
                }
            },
            "timestamp": datetime.now().isoformat()
        }
        
        return jsonify(report)
        
    except Exception as e:
        logger.error(f"获取测试报告失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/test_status', methods=['GET'])
def get_test_status():
    """获取测试状态"""
    try:
        execution_id = request.args.get('execution_id')
        
        # 模拟测试状态
        status = {
            "success": True,
            "execution_id": execution_id,
            "status": {
                "state": "completed",
                "progress": 100,
                "current_test": None,
                "tests_completed": 25,
                "tests_total": 25,
                "start_time": "2024-06-18T12:00:00Z",
                "end_time": "2024-06-18T12:02:30Z",
                "duration": "2.5s"
            },
            "timestamp": datetime.now().isoformat()
        }
        
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"获取测试状态失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    logger.info("启动Test Manager MCP Server...")
    logger.info("服务地址: http://localhost:8097")
    logger.info("API文档: http://localhost:8097/api/status")
    
    app.run(
        host='0.0.0.0',
        port=8097,
        debug=False,
        threaded=True
    )

