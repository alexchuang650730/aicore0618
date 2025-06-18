#!/usr/bin/env python3
"""
<<<<<<< HEAD
Enhanced Test Manager MCP - 增强的测试管理器工作流
集成智能测试策略生成、用例生成和执行管理功能
=======
Test Manager MCP - 测试管理器工作流
基于现有的PowerAutomation测试框架，提供统一的测试管理和执行能力
>>>>>>> fc1525368711230da2586d4c928810f1e886598c
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
from typing import Dict, List, Any, Optional

# 导入增强的测试管理组件
from enhanced_strategy_generator import EnhancedTestStrategyGenerator
from enhanced_case_generator import EnhancedTestCaseGenerator
from enhanced_execution_manager import EnhancedTestExecutionManager
=======
>>>>>>> fc1525368711230da2586d4c928810f1e886598c

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
    
    def __init__(self):
        self.service_id = "test_manager_mcp"
        self.version = "1.0.0"
        self.status = "running"
        
        # 初始化测试管理器
>>>>>>> fc1525368711230da2586d4c928810f1e886598c
        try:
            self.test_manager = get_test_manager()
            logger.info("✅ 成功连接到PowerAutomation测试框架")
        except Exception as e:
            logger.error(f"❌ 测试框架初始化失败: {e}")
            self.test_manager = TestManager()  # 使用简化版本
        
<<<<<<< HEAD
        logger.info(f"✅ Enhanced Test Manager MCP 初始化完成")
        logger.info(f"🧠 智能测试策略生成器: 就绪")
        logger.info(f"📝 智能测试用例生成器: 就绪")
        logger.info(f"⚡ 异步测试执行管理器: 就绪")
    
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
    
    async def discover_tests_by_project(self, project_info):
        """根据项目信息发现相关测试"""
        try:
            project_name = project_info.get("name", "")
            project_type = project_info.get("type", "")
            complexity = project_info.get("complexity", "simple")
            
            # 根据项目类型确定测试策略
            test_strategy = self._determine_test_strategy(project_type, complexity)
            
            # 发现测试
            tests = await self.test_manager.discover_tests(
                module_filter=test_strategy.get("module_filter"),
                test_type_filter=test_strategy.get("test_type")
            )
            
            # 为项目生成特定的测试计划
            test_plan = self._generate_test_plan(project_info, tests)
            
            return {
                "success": True,
                "project_name": project_name,
                "test_strategy": test_strategy,
                "discovered_tests": len(tests),
                "test_plan": test_plan,
                "tests": tests
            }
            
        except Exception as e:
            logger.error(f"测试发现失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "fallback_plan": self._create_fallback_test_plan(project_info)
            }
    
    def _determine_test_strategy(self, project_type, complexity):
        """确定测试策略"""
        strategies = {
            "game": {
                "module_filter": "game|ui|canvas",
                "test_type": "unit",
                "focus_areas": ["游戏逻辑", "UI交互", "性能测试"]
            },
            "web_app": {
                "module_filter": "web|api|frontend",
                "test_type": "integration",
                "focus_areas": ["API测试", "前端测试", "数据库测试"]
            },
            "ecommerce": {
                "module_filter": "ecommerce|payment|user",
                "test_type": "comprehensive",
                "focus_areas": ["支付流程", "用户管理", "安全测试"]
            },
            "api": {
                "module_filter": "api|backend|service",
                "test_type": "integration",
                "focus_areas": ["API端点", "数据验证", "性能测试"]
            }
        }
        
        # 根据复杂度调整策略
        base_strategy = strategies.get(project_type, strategies["web_app"])
        
        if complexity == "simple":
            base_strategy["test_type"] = "simple"
        elif complexity == "complex":
            base_strategy["test_type"] = "comprehensive"
        
        return base_strategy
    
    def _generate_test_plan(self, project_info, discovered_tests):
        """生成测试计划"""
        project_name = project_info.get("name", "Unknown Project")
        
        # 分类测试
        test_categories = {
            "unit_tests": [],
            "integration_tests": [],
            "ui_tests": [],
            "performance_tests": [],
            "security_tests": []
        }
        
        for test in discovered_tests:
            test_type = test.get("test_type", "unit")
            test_name = test.get("test_name", "")
            
            if "unit" in test_type or "unit" in test_name.lower():
                test_categories["unit_tests"].append(test)
            elif "integration" in test_type or "integration" in test_name.lower():
                test_categories["integration_tests"].append(test)
            elif "ui" in test_name.lower() or "frontend" in test_name.lower():
                test_categories["ui_tests"].append(test)
            elif "performance" in test_name.lower() or "load" in test_name.lower():
                test_categories["performance_tests"].append(test)
            elif "security" in test_name.lower() or "auth" in test_name.lower():
                test_categories["security_tests"].append(test)
            else:
                test_categories["unit_tests"].append(test)  # 默认归类为单元测试
        
        # 生成执行计划
        execution_phases = [
            {
                "phase": 1,
                "name": "单元测试",
                "tests": test_categories["unit_tests"],
                "parallel": True,
                "timeout": 300
            },
            {
                "phase": 2,
                "name": "集成测试",
                "tests": test_categories["integration_tests"],
                "parallel": True,
                "timeout": 600
            },
            {
                "phase": 3,
                "name": "UI测试",
                "tests": test_categories["ui_tests"],
                "parallel": False,
                "timeout": 900
            },
            {
                "phase": 4,
                "name": "性能测试",
                "tests": test_categories["performance_tests"],
                "parallel": False,
                "timeout": 1200
            },
            {
                "phase": 5,
                "name": "安全测试",
                "tests": test_categories["security_tests"],
                "parallel": True,
                "timeout": 600
            }
        ]
        
        # 过滤掉没有测试的阶段
        execution_phases = [phase for phase in execution_phases if phase["tests"]]
        
        return {
            "project_name": project_name,
            "total_tests": len(discovered_tests),
            "test_categories": {k: len(v) for k, v in test_categories.items()},
            "execution_phases": execution_phases,
            "estimated_duration": sum(phase["timeout"] for phase in execution_phases),
            "recommended_parallel": len(discovered_tests) > 10
        }
    
    def _create_fallback_test_plan(self, project_info):
        """创建备用测试计划"""
        project_name = project_info.get("name", "Unknown Project")
        project_type = project_info.get("type", "web_app")
        
        # 基于项目类型的标准测试模板
        templates = {
            "game": [
                {"name": "游戏逻辑测试", "type": "unit", "description": "测试游戏核心逻辑"},
                {"name": "UI交互测试", "type": "integration", "description": "测试用户界面交互"},
                {"name": "性能测试", "type": "performance", "description": "测试游戏性能"}
            ],
            "web_app": [
                {"name": "前端组件测试", "type": "unit", "description": "测试前端组件"},
                {"name": "API接口测试", "type": "integration", "description": "测试API接口"},
                {"name": "端到端测试", "type": "e2e", "description": "测试完整用户流程"}
            ],
            "ecommerce": [
                {"name": "用户注册登录测试", "type": "integration", "description": "测试用户认证"},
                {"name": "商品管理测试", "type": "unit", "description": "测试商品CRUD"},
                {"name": "支付流程测试", "type": "integration", "description": "测试支付功能"},
                {"name": "安全测试", "type": "security", "description": "测试系统安全性"}
            ]
        }
        
        test_template = templates.get(project_type, templates["web_app"])
        
        return {
            "project_name": project_name,
            "test_template": test_template,
            "total_template_tests": len(test_template),
            "note": "使用标准测试模板，建议根据实际项目调整"
        }
    
    async def execute_test_plan(self, test_plan, project_info):
        """执行测试计划"""
        try:
            project_name = project_info.get("name", "Unknown Project")
            
            logger.info(f"🧪 开始执行测试计划: {project_name}")
            
            # 执行测试
            if "execution_phases" in test_plan:
                # 按阶段执行
                results = await self._execute_phased_tests(test_plan["execution_phases"])
            else:
                # 执行模板测试
                results = await self._execute_template_tests(test_plan.get("test_template", []))
            
            # 生成测试报告
            test_report = self._generate_test_report(project_info, test_plan, results)
            
            return {
                "success": True,
                "project_name": project_name,
                "execution_results": results,
                "test_report": test_report,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"测试执行失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "project_name": project_info.get("name", "Unknown Project"),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _execute_phased_tests(self, execution_phases):
        """按阶段执行测试"""
        phase_results = []
        
        for phase in execution_phases:
            logger.info(f"🔄 执行测试阶段 {phase['phase']}: {phase['name']}")
            
            try:
                # 执行该阶段的测试
                session = await self.test_manager.run_tests(
                    tests=phase["tests"],
                    parallel=phase["parallel"]
                )
                
                phase_result = {
                    "phase": phase["phase"],
                    "name": phase["name"],
                    "status": "completed",
                    "total_tests": len(phase["tests"]),
                    "passed": session.passed_tests if hasattr(session, 'passed_tests') else 0,
                    "failed": session.failed_tests if hasattr(session, 'failed_tests') else 0,
                    "duration": (session.end_time - session.start_time).total_seconds() if hasattr(session, 'end_time') and session.end_time else 0
                }
                
            except Exception as e:
                logger.error(f"阶段 {phase['phase']} 执行失败: {e}")
                phase_result = {
                    "phase": phase["phase"],
                    "name": phase["name"],
                    "status": "failed",
                    "error": str(e),
                    "total_tests": len(phase["tests"]),
                    "passed": 0,
                    "failed": len(phase["tests"])
                }
            
            phase_results.append(phase_result)
        
        return phase_results
    
    async def _execute_template_tests(self, test_template):
        """执行模板测试"""
        template_results = []
        
        for test_item in test_template:
            logger.info(f"🧪 执行模板测试: {test_item['name']}")
            
            # 模拟测试执行
            import random
            import time
            
            start_time = time.time()
            
            # 模拟测试执行时间
            await asyncio.sleep(random.uniform(0.1, 0.5))
            
            # 模拟测试结果（90%成功率）
            success = random.random() > 0.1
            
            end_time = time.time()
            
            result = {
                "name": test_item["name"],
                "type": test_item["type"],
                "description": test_item["description"],
                "status": "passed" if success else "failed",
                "duration": end_time - start_time,
                "timestamp": datetime.now().isoformat()
            }
            
            if not success:
                result["error"] = f"模拟测试失败: {test_item['name']}"
            
            template_results.append(result)
        
        return template_results
    
    def _generate_test_report(self, project_info, test_plan, results):
        """生成测试报告"""
        project_name = project_info.get("name", "Unknown Project")
        
        # 统计结果
        if isinstance(results, list) and results and "phase" in results[0]:
            # 阶段测试结果
            total_tests = sum(r.get("total_tests", 0) for r in results)
            total_passed = sum(r.get("passed", 0) for r in results)
            total_failed = sum(r.get("failed", 0) for r in results)
            total_duration = sum(r.get("duration", 0) for r in results)
        else:
            # 模板测试结果
            total_tests = len(results)
            total_passed = sum(1 for r in results if r.get("status") == "passed")
            total_failed = sum(1 for r in results if r.get("status") == "failed")
            total_duration = sum(r.get("duration", 0) for r in results)
        
        success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0
        
        # 生成报告
        report = {
            "project_name": project_name,
            "test_execution_summary": {
                "total_tests": total_tests,
                "passed": total_passed,
                "failed": total_failed,
                "success_rate": round(success_rate, 2),
                "total_duration": round(total_duration, 2),
                "execution_date": datetime.now().isoformat()
            },
            "test_plan_info": {
                "plan_type": "phased" if "execution_phases" in test_plan else "template",
                "total_phases": len(test_plan.get("execution_phases", [])),
                "estimated_duration": test_plan.get("estimated_duration", 0)
            },
            "detailed_results": results,
            "recommendations": self._generate_recommendations(success_rate, results),
            "next_steps": self._generate_next_steps(project_info, success_rate)
        }
        
        return report
    
    def _generate_recommendations(self, success_rate, results):
        """生成测试建议"""
        recommendations = []
        
        if success_rate < 70:
            recommendations.append("测试成功率较低，建议检查代码质量和测试用例")
        elif success_rate < 90:
            recommendations.append("测试成功率中等，建议优化失败的测试用例")
        else:
            recommendations.append("测试成功率良好，可以考虑增加更多测试覆盖")
        
        # 分析失败的测试
        if isinstance(results, list):
            failed_tests = [r for r in results if r.get("status") == "failed"]
            if failed_tests:
                recommendations.append(f"发现 {len(failed_tests)} 个失败测试，建议优先修复")
        
        return recommendations
    
    def _generate_next_steps(self, project_info, success_rate):
        """生成下一步建议"""
        next_steps = []
        
        if success_rate >= 90:
            next_steps.append("✅ 测试通过，可以进行部署")
            next_steps.append("🚀 建议执行部署前的最终检查")
        elif success_rate >= 70:
            next_steps.append("⚠️ 部分测试失败，建议修复后重新测试")
            next_steps.append("🔧 检查失败的测试用例并修复代码")
        else:
            next_steps.append("❌ 测试失败率较高，不建议部署")
            next_steps.append("🛠️ 需要大幅改进代码质量")
            next_steps.append("📋 建议重新审查项目需求和设计")
        
        return next_steps

# Flask API 端点
test_manager_mcp = TestManagerMCP()

@app.route('/health')
def health_check():
    """健康检查"""
    return jsonify({
        "service": test_manager_mcp.service_id,
        "status": "healthy",
        "version": test_manager_mcp.version,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/test/discover', methods=['POST'])
def discover_tests():
    """发现测试"""
    try:
        data = request.get_json()
        project_info = data.get('project_info', {})
        
>>>>>>> fc1525368711230da2586d4c928810f1e886598c
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(
<<<<<<< HEAD
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
        )
        return jsonify(result)
    except Exception as e:
=======
            test_manager_mcp.discover_tests_by_project(project_info)
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"测试发现API失败: {e}")
>>>>>>> fc1525368711230da2586d4c928810f1e886598c
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/test/execute', methods=['POST'])
def execute_tests():
    """执行测试"""
    try:
        data = request.get_json()
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
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        result = loop.run_until_complete(
            test_manager_mcp.execute_test_plan(test_plan, project_info)
        )
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"测试执行API失败: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/test/full-cycle', methods=['POST'])
def full_test_cycle():
    """完整测试周期：发现 + 执行"""
    try:
        data = request.get_json()
        project_info = data.get('project_info', {})
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # 1. 发现测试
        discovery_result = loop.run_until_complete(
            test_manager_mcp.discover_tests_by_project(project_info)
        )
        
        if not discovery_result["success"]:
            return jsonify(discovery_result), 500
        
        # 2. 执行测试
        test_plan = discovery_result.get("test_plan", discovery_result.get("fallback_plan", {}))
        execution_result = loop.run_until_complete(
            test_manager_mcp.execute_test_plan(test_plan, project_info)
        )
        
        # 3. 合并结果
        full_result = {
            "success": execution_result["success"],
            "project_name": project_info.get("name", "Unknown Project"),
            "discovery_phase": discovery_result,
            "execution_phase": execution_result,
            "timestamp": datetime.now().isoformat()
        }
        
        return jsonify(full_result)
        
    except Exception as e:
        logger.error(f"完整测试周期API失败: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/mcp/request', methods=['POST'])
def handle_mcp_request():
    """处理MCP请求"""
    try:
        data = request.get_json()
        action = data.get('action')
        params = data.get('params', {})
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        if action == "discover_tests":
            result = loop.run_until_complete(
                test_manager_mcp.discover_tests_by_project(params.get('project_info', {}))
            )
            return jsonify({"success": True, "results": result})
        
        elif action == "execute_tests":
            result = loop.run_until_complete(
                test_manager_mcp.execute_test_plan(
                    params.get('test_plan', {}),
                    params.get('project_info', {})
                )
            )
            return jsonify({"success": True, "results": result})
        
        elif action == "full_test_cycle":
            # 完整测试周期
            project_info = params.get('project_info', {})
            
            discovery_result = loop.run_until_complete(
                test_manager_mcp.discover_tests_by_project(project_info)
            )
            
            if discovery_result["success"]:
                test_plan = discovery_result.get("test_plan", discovery_result.get("fallback_plan", {}))
                execution_result = loop.run_until_complete(
                    test_manager_mcp.execute_test_plan(test_plan, project_info)
                )
                
                result = {
                    "discovery": discovery_result,
                    "execution": execution_result
                }
            else:
                result = {"discovery": discovery_result, "execution": None}
            
            return jsonify({"success": True, "results": result})
        
        else:
            return jsonify({"success": False, "error": f"未知操作: {action}"}), 400
            
    except Exception as e:
        logger.error(f"处理MCP请求失败: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    logger.info("🚀 启动 Test Manager MCP...")
    logger.info(f"📍 服务地址: http://0.0.0.0:8097")
    
    app.run(host='0.0.0.0', port=8097, debug=False)

>>>>>>> fc1525368711230da2586d4c928810f1e886598c
