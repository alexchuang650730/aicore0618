#!/usr/bin/env python3
"""
<<<<<<< HEAD
<<<<<<< HEAD
Enhanced Test Manager MCP - 增强的测试管理器工作流
集成智能测试策略生成、用例生成和执行管理功能
=======
Test Manager MCP - 测试管理器工作流
基于现有的PowerAutomation测试框架，提供统一的测试管理和执行能力
>>>>>>> fc1525368711230da2586d4c928810f1e886598c
=======
Enhanced Test Manager MCP - 增强的测试管理器工作流
集成智能测试策略生成、用例生成和执行管理功能
>>>>>>> 0e3116c98243b7e7fddeb0eae422619dece7f4fd
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
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> 0e3116c98243b7e7fddeb0eae422619dece7f4fd
from typing import Dict, List, Any, Optional

# 导入增强的测试管理组件
from enhanced_strategy_generator import EnhancedTestStrategyGenerator
from enhanced_case_generator import EnhancedTestCaseGenerator
from enhanced_execution_manager import EnhancedTestExecutionManager
<<<<<<< HEAD
=======
>>>>>>> fc1525368711230da2586d4c928810f1e886598c
=======
>>>>>>> 0e3116c98243b7e7fddeb0eae422619dece7f4fd

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

<<<<<<< HEAD
<<<<<<< HEAD
class EnhancedTestManagerMCP:
    """增强的测试管理器MCP - 集成智能测试管理能力"""
    
    def __init__(self):
        self.service_id = "enhanced_test_manager_mcp"
        self.version = "2.0.0"
        self.status = "running"
        
        # 初始化增强组件
        self.strategy_generator = EnhancedTestStrategyGenerator()
        self.case_generator = EnhancedTestCaseGenerator()
        self.execution_manager = EnhancedTestExecutionManager()
        
        # 初始化原有测试管理器
=======
class TestManagerMCP:
    """测试管理器MCP - 包装现有的测试框架"""
=======
class EnhancedTestManagerMCP:
    """增强的测试管理器MCP - 集成智能测试管理能力"""
>>>>>>> 0e3116c98243b7e7fddeb0eae422619dece7f4fd
    
    def __init__(self):
        self.service_id = "enhanced_test_manager_mcp"
        self.version = "2.0.0"
        self.status = "running"
        
<<<<<<< HEAD
        # 初始化测试管理器
>>>>>>> fc1525368711230da2586d4c928810f1e886598c
=======
        # 初始化增强组件
        self.strategy_generator = EnhancedTestStrategyGenerator()
        self.case_generator = EnhancedTestCaseGenerator()
        self.execution_manager = EnhancedTestExecutionManager()
        
        # 初始化原有测试管理器
>>>>>>> 0e3116c98243b7e7fddeb0eae422619dece7f4fd
        try:
            self.test_manager = get_test_manager()
            logger.info("✅ 成功连接到PowerAutomation测试框架")
        except Exception as e:
            logger.error(f"❌ 测试框架初始化失败: {e}")
            self.test_manager = TestManager()  # 使用简化版本
        
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> 0e3116c98243b7e7fddeb0eae422619dece7f4fd
        logger.info(f"✅ Enhanced Test Manager MCP 初始化完成")
        logger.info(f"🧠 智能测试策略生成器: 就绪")
        logger.info(f"📝 智能测试用例生成器: 就绪")
        logger.info(f"⚡ 异步测试执行管理器: 就绪")
<<<<<<< HEAD
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """处理测试管理请求 - 增强版本"""
        request_type = data.get("type")
        
        try:
            if request_type == "generate_strategy":
                return await self.strategy_generator.generate_strategy_for_remote(
                    data.get("project_info", {})
                )
            elif request_type == "generate_cases":
                return await self.case_generator.generate_cases_for_remote(
                    data.get("strategy", {}),
                    data.get("requirements", {})
                )
            elif request_type == "execute_tests":
                execution_id = await self.execution_manager.execute_for_remote(
                    data.get("test_cases", []),
                    data.get("execution_config", {})
                )
                return {
                    "success": True,
                    "execution_id": execution_id,
                    "message": "测试执行已启动"
                }
            elif request_type == "get_execution_status":
                return self.execution_manager.get_execution_status(
                    data.get("execution_id")
                )
            elif request_type == "get_execution_report":
                return self.execution_manager.get_execution_report(
                    data.get("execution_id")
                )
            elif request_type == "get_active_executions":
                return {
                    "success": True,
                    "active_executions": self.execution_manager.get_active_executions()
                }
            elif request_type == "cancel_execution":
                success = await self.execution_manager.cancel_execution(
                    data.get("execution_id")
                )
                return {
                    "success": success,
                    "message": "执行已取消" if success else "执行未找到或无法取消"
                }
            elif request_type == "full_intelligent_cycle":
                # 完整智能测试周期
                return await self._execute_full_intelligent_cycle(data)
            else:
                # 回退到原有功能
                return await self._handle_legacy_request(request_type, data)
                
        except Exception as e:
            logger.error(f"处理请求失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "request_type": request_type
            }
    
    async def _execute_full_intelligent_cycle(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """执行完整的智能测试周期"""
        project_info = data.get("project_info", {})
        
        try:
            # 1. 生成智能测试策略
            logger.info("🧠 生成智能测试策略...")
            strategy_result = await self.strategy_generator.generate_strategy_for_remote(project_info)
            
            if not strategy_result.get("success", False):
                return {
                    "success": False,
                    "error": "测试策略生成失败",
                    "details": strategy_result
                }
            
            # 2. 生成智能测试用例
            logger.info("📝 生成智能测试用例...")
            cases_result = await self.case_generator.generate_cases_for_remote(
                strategy_result,
                data.get("requirements", {})
            )
            
            if not cases_result.get("success", False):
                return {
                    "success": False,
                    "error": "测试用例生成失败",
                    "details": cases_result
                }
            
            # 3. 执行测试
            logger.info("⚡ 启动智能测试执行...")
            execution_config = data.get("execution_config", {"mode": "mixed"})
            execution_id = await self.execution_manager.execute_for_remote(
                cases_result.get("test_cases", []),
                execution_config
            )
            
            return {
                "success": True,
                "cycle_id": f"intelligent_cycle_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "strategy": strategy_result,
                "test_cases": cases_result,
                "execution": {
                    "execution_id": execution_id,
                    "status": "started",
                    "message": "智能测试执行已启动"
                },
                "summary": {
                    "total_test_cases": cases_result.get("total_cases", 0),
                    "coverage_target": strategy_result.get("coverage_target", 0),
                    "estimated_duration": cases_result.get("estimated_execution_time", {}),
                    "automation_rate": cases_result.get("automation_rate", 0)
                }
            }
            
        except Exception as e:
            logger.error(f"智能测试周期执行失败: {e}")
            return {
                "success": False,
                "error": f"智能测试周期执行失败: {e}"
            }
    
    async def _handle_legacy_request(self, request_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """处理原有的请求类型"""
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
# 创建增强的测试管理器实例
enhanced_test_manager_mcp = EnhancedTestManagerMCP()

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        "service": enhanced_test_manager_mcp.service_id,
        "version": enhanced_test_manager_mcp.version,
        "status": enhanced_test_manager_mcp.status,
        "timestamp": datetime.now().isoformat(),
        "capabilities": [
            "智能测试策略生成",
            "智能测试用例生成", 
            "异步测试执行管理",
            "实时状态监控",
            "详细报告生成"
        ]
    })

@app.route('/api/test/strategy', methods=['POST'])
def generate_strategy():
    """生成测试策略"""
    try:
        data = request.get_json()
=======
        # 测试类型映射
        self.test_type_mapping = {
            "unit": "unit",
            "integration": "integration", 
            "comprehensive": "comprehensive",
            "smoke": "simple",
            "all": None
        }
        
        logger.info(f"✅ Test Manager MCP 初始化完成")
=======
>>>>>>> 0e3116c98243b7e7fddeb0eae422619dece7f4fd
    
    async def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """处理测试管理请求 - 增强版本"""
        request_type = data.get("type")
        
        try:
            if request_type == "generate_strategy":
                return await self.strategy_generator.generate_strategy_for_remote(
                    data.get("project_info", {})
                )
            elif request_type == "generate_cases":
                return await self.case_generator.generate_cases_for_remote(
                    data.get("strategy", {}),
                    data.get("requirements", {})
                )
            elif request_type == "execute_tests":
                execution_id = await self.execution_manager.execute_for_remote(
                    data.get("test_cases", []),
                    data.get("execution_config", {})
                )
                return {
                    "success": True,
                    "execution_id": execution_id,
                    "message": "测试执行已启动"
                }
            elif request_type == "get_execution_status":
                return self.execution_manager.get_execution_status(
                    data.get("execution_id")
                )
            elif request_type == "get_execution_report":
                return self.execution_manager.get_execution_report(
                    data.get("execution_id")
                )
            elif request_type == "get_active_executions":
                return {
                    "success": True,
                    "active_executions": self.execution_manager.get_active_executions()
                }
            elif request_type == "cancel_execution":
                success = await self.execution_manager.cancel_execution(
                    data.get("execution_id")
                )
                return {
                    "success": success,
                    "message": "执行已取消" if success else "执行未找到或无法取消"
                }
            elif request_type == "full_intelligent_cycle":
                # 完整智能测试周期
                return await self._execute_full_intelligent_cycle(data)
            else:
                # 回退到原有功能
                return await self._handle_legacy_request(request_type, data)
                
        except Exception as e:
            logger.error(f"处理请求失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "request_type": request_type
            }
    
    async def _execute_full_intelligent_cycle(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """执行完整的智能测试周期"""
        project_info = data.get("project_info", {})
        
        try:
            # 1. 生成智能测试策略
            logger.info("🧠 生成智能测试策略...")
            strategy_result = await self.strategy_generator.generate_strategy_for_remote(project_info)
            
            if not strategy_result.get("success", False):
                return {
                    "success": False,
                    "error": "测试策略生成失败",
                    "details": strategy_result
                }
            
            # 2. 生成智能测试用例
            logger.info("📝 生成智能测试用例...")
            cases_result = await self.case_generator.generate_cases_for_remote(
                strategy_result,
                data.get("requirements", {})
            )
            
            if not cases_result.get("success", False):
                return {
                    "success": False,
                    "error": "测试用例生成失败",
                    "details": cases_result
                }
            
            # 3. 执行测试
            logger.info("⚡ 启动智能测试执行...")
            execution_config = data.get("execution_config", {"mode": "mixed"})
            execution_id = await self.execution_manager.execute_for_remote(
                cases_result.get("test_cases", []),
                execution_config
            )
            
            return {
                "success": True,
                "cycle_id": f"intelligent_cycle_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "strategy": strategy_result,
                "test_cases": cases_result,
                "execution": {
                    "execution_id": execution_id,
                    "status": "started",
                    "message": "智能测试执行已启动"
                },
                "summary": {
                    "total_test_cases": cases_result.get("total_cases", 0),
                    "coverage_target": strategy_result.get("coverage_target", 0),
                    "estimated_duration": cases_result.get("estimated_execution_time", {}),
                    "automation_rate": cases_result.get("automation_rate", 0)
                }
            }
            
        except Exception as e:
            logger.error(f"智能测试周期执行失败: {e}")
            return {
                "success": False,
                "error": f"智能测试周期执行失败: {e}"
            }
    
    async def _handle_legacy_request(self, request_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """处理原有的请求类型"""
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
# 创建增强的测试管理器实例
enhanced_test_manager_mcp = EnhancedTestManagerMCP()

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        "service": enhanced_test_manager_mcp.service_id,
        "version": enhanced_test_manager_mcp.version,
        "status": enhanced_test_manager_mcp.status,
        "timestamp": datetime.now().isoformat(),
        "capabilities": [
            "智能测试策略生成",
            "智能测试用例生成", 
            "异步测试执行管理",
            "实时状态监控",
            "详细报告生成"
        ]
    })

@app.route('/api/test/strategy', methods=['POST'])
def generate_strategy():
    """生成测试策略"""
    try:
        data = request.get_json()
<<<<<<< HEAD
        project_info = data.get('project_info', {})
        
>>>>>>> fc1525368711230da2586d4c928810f1e886598c
=======
>>>>>>> 0e3116c98243b7e7fddeb0eae422619dece7f4fd
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(
<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> 0e3116c98243b7e7fddeb0eae422619dece7f4fd
            enhanced_test_manager_mcp.strategy_generator.generate_strategy_for_remote(
                data.get('project_info', {})
            )
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/test/cases', methods=['POST'])
def generate_cases():
    """生成测试用例"""
    try:
        data = request.get_json()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(
            enhanced_test_manager_mcp.case_generator.generate_cases_for_remote(
                data.get('strategy', {}),
                data.get('requirements', {})
            )
<<<<<<< HEAD
        )
        return jsonify(result)
    except Exception as e:
=======
            test_manager_mcp.discover_tests_by_project(project_info)
=======
>>>>>>> 0e3116c98243b7e7fddeb0eae422619dece7f4fd
        )
        return jsonify(result)
    except Exception as e:
<<<<<<< HEAD
        logger.error(f"测试发现API失败: {e}")
>>>>>>> fc1525368711230da2586d4c928810f1e886598c
=======
>>>>>>> 0e3116c98243b7e7fddeb0eae422619dece7f4fd
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/test/execute', methods=['POST'])
def execute_tests():
    """执行测试"""
    try:
        data = request.get_json()
<<<<<<< HEAD
<<<<<<< HEAD
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        execution_id = loop.run_until_complete(
            enhanced_test_manager_mcp.execution_manager.execute_for_remote(
                data.get('test_cases', []),
                data.get('execution_config', {})
            )
        )
        return jsonify({
            "success": True,
            "execution_id": execution_id,
            "message": "测试执行已启动"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/test/status/<execution_id>', methods=['GET'])
def get_execution_status(execution_id):
    """获取执行状态"""
    try:
        result = enhanced_test_manager_mcp.execution_manager.get_execution_status(execution_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/test/report/<execution_id>', methods=['GET'])
def get_execution_report(execution_id):
    """获取执行报告"""
    try:
        result = enhanced_test_manager_mcp.execution_manager.get_execution_report(execution_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/test/executions', methods=['GET'])
def get_active_executions():
    """获取活跃执行"""
    try:
        result = enhanced_test_manager_mcp.execution_manager.get_active_executions()
        return jsonify({"success": True, "active_executions": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/test/intelligent-cycle', methods=['POST'])
def execute_intelligent_cycle():
    """执行完整智能测试周期"""
    try:
        data = request.get_json()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(
            enhanced_test_manager_mcp._execute_full_intelligent_cycle(data)
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/mcp/process', methods=['POST'])
def process_mcp_request():
    """处理MCP请求 - 兼容原有接口"""
    try:
        data = request.get_json()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(
            enhanced_test_manager_mcp.process(data)
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    logger.info("🚀 启动 Enhanced Test Manager MCP...")
    logger.info(f"📍 服务地址: http://0.0.0.0:8097")
    logger.info(f"🧠 智能测试策略生成: /api/test/strategy")
    logger.info(f"📝 智能测试用例生成: /api/test/cases")
    logger.info(f"⚡ 异步测试执行: /api/test/execute")
    logger.info(f"📊 完整智能周期: /api/test/intelligent-cycle")
    
    app.run(host='0.0.0.0', port=8097, debug=False)
=======
        test_plan = data.get('test_plan', {})
        project_info = data.get('project_info', {})
=======
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
>>>>>>> 0e3116c98243b7e7fddeb0eae422619dece7f4fd
        
        execution_id = loop.run_until_complete(
            enhanced_test_manager_mcp.execution_manager.execute_for_remote(
                data.get('test_cases', []),
                data.get('execution_config', {})
            )
        )
        return jsonify({
            "success": True,
            "execution_id": execution_id,
            "message": "测试执行已启动"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/test/status/<execution_id>', methods=['GET'])
def get_execution_status(execution_id):
    """获取执行状态"""
    try:
        result = enhanced_test_manager_mcp.execution_manager.get_execution_status(execution_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/test/report/<execution_id>', methods=['GET'])
def get_execution_report(execution_id):
    """获取执行报告"""
    try:
        result = enhanced_test_manager_mcp.execution_manager.get_execution_report(execution_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/test/executions', methods=['GET'])
def get_active_executions():
    """获取活跃执行"""
    try:
        result = enhanced_test_manager_mcp.execution_manager.get_active_executions()
        return jsonify({"success": True, "active_executions": result})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/test/intelligent-cycle', methods=['POST'])
def execute_intelligent_cycle():
    """执行完整智能测试周期"""
    try:
        data = request.get_json()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(
            enhanced_test_manager_mcp._execute_full_intelligent_cycle(data)
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/mcp/process', methods=['POST'])
def process_mcp_request():
    """处理MCP请求 - 兼容原有接口"""
    try:
        data = request.get_json()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(
            enhanced_test_manager_mcp.process(data)
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    logger.info("🚀 启动 Enhanced Test Manager MCP...")
    logger.info(f"📍 服务地址: http://0.0.0.0:8097")
    logger.info(f"🧠 智能测试策略生成: /api/test/strategy")
    logger.info(f"📝 智能测试用例生成: /api/test/cases")
    logger.info(f"⚡ 异步测试执行: /api/test/execute")
    logger.info(f"📊 完整智能周期: /api/test/intelligent-cycle")
    
    app.run(host='0.0.0.0', port=8097, debug=False)
<<<<<<< HEAD

>>>>>>> fc1525368711230da2586d4c928810f1e886598c
=======
>>>>>>> 0e3116c98243b7e7fddeb0eae422619dece7f4fd
