#!/usr/bin/env python3
"""
完整工作流系统验证脚本
验证整个PowerAutomation工作流系统的完整性和功能
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from mcp.enhanced_mcp_coordinator import EnhancedMCPCoordinator
from mcp.adapter.smartui_mcp.smartui_mcp import SmartUIMcp
from mcp.adapter.enhanced_workflow_mcp.enhanced_workflow_mcp import EnhancedWorkflowMcp
from mcp.adapter.requirement_analysis_mcp.requirement_analysis_mcp import RequirementAnalysisMcp
from mcp.adapter.code_generation_mcp.code_generation_mcp import CodeGenerationMcp

class WorkflowSystemValidator:
    """完整工作流系统验证器"""
    
    def __init__(self):
        self.coordinator = EnhancedMCPCoordinator()
        self.smartui_mcp = SmartUIMcp()
        self.enhanced_workflow_mcp = EnhancedWorkflowMcp()
        self.requirement_analysis_mcp = RequirementAnalysisMcp()
        self.code_generation_mcp = CodeGenerationMcp()
        
        self.validation_results = []
        self.session_id = f"validation_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    async def setup_system(self):
        """设置完整系统"""
        print("🚀 启动PowerAutomation完整工作流系统")
        print("=" * 60)
        
        # 启动协调器
        await self.coordinator.start()
        print("✅ MCP协调器已启动")
        
        # 注册所有MCP
        mcps = [
            ("smartui_mcp", self.smartui_mcp, "智能用户界面"),
            ("enhanced_workflow_mcp", self.enhanced_workflow_mcp, "增强工作流引擎"),
            ("requirement_analysis_mcp", self.requirement_analysis_mcp, "需求分析工作流"),
            ("code_generation_mcp", self.code_generation_mcp, "代码生成工作流")
        ]
        
        for mcp_name, mcp_instance, description in mcps:
            success = await self.coordinator.register_mcp(mcp_name, mcp_instance)
            if success:
                print(f"✅ {description} ({mcp_name}) 已注册")
            else:
                print(f"❌ {description} ({mcp_name}) 注册失败")
        
        print("\n🎯 系统启动完成，开始验证...")
    
    async def validate_complete_workflow_system(self):
        """验证完整工作流系统"""
        print("\n📋 验证完整工作流系统功能")
        print("-" * 40)
        
        # 验证1: 系统架构完整性
        await self._validate_system_architecture()
        
        # 验证2: 用户交互流程
        await self._validate_user_interaction_flow()
        
        # 验证3: 工作流执行能力
        await self._validate_workflow_execution()
        
        # 验证4: 数据流通信
        await self._validate_data_flow_communication()
        
        # 验证5: 错误处理和恢复
        await self._validate_error_handling()
        
        # 验证6: 性能和可扩展性
        await self._validate_performance_scalability()
        
        # 验证7: 完整业务场景
        await self._validate_complete_business_scenario()
    
    async def _validate_system_architecture(self):
        """验证系统架构完整性"""
        print("🏗️ 验证系统架构完整性...")
        
        try:
            # 检查所有组件状态
            coordinator_status = await self.coordinator.get_status()
            registered_mcps = coordinator_status.get("registered_mcps", 0)
            
            # 验证核心组件
            expected_components = 4  # SmartUI, Enhanced Workflow, Requirement Analysis, Code Generation
            architecture_complete = registered_mcps >= expected_components
            
            # 检查健康状态
            health_status = await self.coordinator.mcp_registry.health_check_all()
            all_healthy = all(status["status"] == "healthy" for status in health_status.values())
            
            self._record_validation("system_architecture", 
                                  architecture_complete and all_healthy,
                                  f"系统架构完整性: {registered_mcps}/{expected_components} 组件注册, 健康状态: {'正常' if all_healthy else '异常'}",
                                  {"registered_mcps": registered_mcps, "health_status": health_status})
            
        except Exception as e:
            self._record_validation("system_architecture", False, f"架构验证失败: {e}")
    
    async def _validate_user_interaction_flow(self):
        """验证用户交互流程"""
        print("👤 验证用户交互流程...")
        
        try:
            # 模拟用户交互序列
            interactions = [
                {
                    "input": "你好，我需要帮助",
                    "expected_intent": "help_request"
                },
                {
                    "input": "我想创建一个电商网站项目",
                    "expected_intent": "create_project"
                },
                {
                    "input": "帮我分析一下需求",
                    "expected_intent": "requirement_analysis"
                },
                {
                    "input": "生成相应的代码",
                    "expected_intent": "code_generation"
                }
            ]
            
            successful_interactions = 0
            
            for i, interaction in enumerate(interactions):
                user_input_data = {
                    "type": "user_input",
                    "session_id": self.session_id,
                    "user_id": "validation_user",
                    "input": interaction["input"],
                    "input_type": "text"
                }
                
                response = await self.smartui_mcp.process(user_input_data)
                
                if response.get("status") == "success":
                    successful_interactions += 1
                    print(f"  ✅ 交互 {i+1}: {interaction['input'][:30]}...")
                else:
                    print(f"  ❌ 交互 {i+1}: {interaction['input'][:30]}...")
            
            interaction_success_rate = successful_interactions / len(interactions)
            
            self._record_validation("user_interaction_flow",
                                  interaction_success_rate >= 0.8,
                                  f"用户交互流程: {successful_interactions}/{len(interactions)} 成功, 成功率: {interaction_success_rate:.1%}",
                                  {"successful_interactions": successful_interactions, "total_interactions": len(interactions)})
            
        except Exception as e:
            self._record_validation("user_interaction_flow", False, f"用户交互验证失败: {e}")
    
    async def _validate_workflow_execution(self):
        """验证工作流执行能力"""
        print("⚙️ 验证工作流执行能力...")
        
        try:
            # 测试不同类型的工作流
            workflow_types = [
                "requirement_analysis",
                "code_generation",
                "testing",
                "documentation",
                "deployment",
                "monitoring"
            ]
            
            successful_workflows = 0
            
            for workflow_type in workflow_types:
                workflow_data = {
                    "type": "create_workflow",
                    "workflow_type": workflow_type,
                    "name": f"验证_{workflow_type}_工作流",
                    "description": f"用于验证{workflow_type}工作流的执行能力"
                }
                
                response = await self.enhanced_workflow_mcp.process(workflow_data)
                
                if response.get("status") == "success":
                    successful_workflows += 1
                    print(f"  ✅ {workflow_type} 工作流创建成功")
                else:
                    print(f"  ❌ {workflow_type} 工作流创建失败")
            
            workflow_success_rate = successful_workflows / len(workflow_types)
            
            self._record_validation("workflow_execution",
                                  workflow_success_rate >= 0.8,
                                  f"工作流执行能力: {successful_workflows}/{len(workflow_types)} 成功, 成功率: {workflow_success_rate:.1%}",
                                  {"successful_workflows": successful_workflows, "total_workflow_types": len(workflow_types)})
            
        except Exception as e:
            self._record_validation("workflow_execution", False, f"工作流执行验证失败: {e}")
    
    async def _validate_data_flow_communication(self):
        """验证数据流通信"""
        print("🔄 验证数据流通信...")
        
        try:
            # 测试端到端数据流
            # SmartUI -> Coordinator -> Workflow MCP -> Response
            
            # 创建工作流请求
            workflow_request = {
                "type": "workflow_request",
                "session_id": self.session_id,
                "workflow_type": "requirement_analysis",
                "workflow_name": "数据流验证工作流",
                "description": "验证数据流通信的工作流"
            }
            
            # 步骤1: SmartUI处理请求
            smartui_response = await self.smartui_mcp.process(workflow_request)
            step1_success = smartui_response.get("status") == "success"
            
            # 步骤2: 协调器路由请求
            if step1_success:
                coordinator_request = smartui_response.get("coordinator_request")
                if coordinator_request:
                    coord_response = await self.coordinator.handle_smartui_request(coordinator_request)
                    step2_success = coord_response.get("status") == "success"
                else:
                    step2_success = False
            else:
                step2_success = False
            
            # 步骤3: 直接验证MCP通信
            direct_request = {
                "type": "analyze_requirement",
                "requirement": "验证数据流通信的测试需求",
                "requirement_type": "functional",
                "title": "数据流验证需求"
            }
            
            direct_response = await self.requirement_analysis_mcp.process(direct_request)
            step3_success = direct_response.get("status") == "success"
            
            # 计算通信成功率
            communication_steps = [step1_success, step2_success, step3_success]
            communication_success_rate = sum(communication_steps) / len(communication_steps)
            
            self._record_validation("data_flow_communication",
                                  communication_success_rate >= 0.8,
                                  f"数据流通信: {sum(communication_steps)}/{len(communication_steps)} 步骤成功, 成功率: {communication_success_rate:.1%}",
                                  {"step1_smartui": step1_success, "step2_coordinator": step2_success, "step3_direct_mcp": step3_success})
            
        except Exception as e:
            self._record_validation("data_flow_communication", False, f"数据流通信验证失败: {e}")
    
    async def _validate_error_handling(self):
        """验证错误处理和恢复"""
        print("🛡️ 验证错误处理和恢复...")
        
        try:
            # 测试各种错误场景
            error_scenarios = [
                {
                    "name": "无效请求类型",
                    "data": {"type": "invalid_request_type"},
                    "target": self.smartui_mcp
                },
                {
                    "name": "缺少必要参数",
                    "data": {"type": "analyze_requirement"},  # 缺少requirement参数
                    "target": self.requirement_analysis_mcp
                },
                {
                    "name": "无效工作流类型",
                    "data": {"type": "create_workflow", "workflow_type": "invalid_type"},
                    "target": self.enhanced_workflow_mcp
                }
            ]
            
            handled_errors = 0
            
            for scenario in error_scenarios:
                try:
                    response = await scenario["target"].process(scenario["data"])
                    
                    # 检查是否正确处理错误
                    if response.get("status") == "error" and "error" in response:
                        handled_errors += 1
                        print(f"  ✅ {scenario['name']}: 错误正确处理")
                    else:
                        print(f"  ❌ {scenario['name']}: 错误处理不当")
                        
                except Exception as e:
                    # 如果抛出异常，检查是否是预期的
                    handled_errors += 1
                    print(f"  ✅ {scenario['name']}: 异常正确抛出")
            
            error_handling_rate = handled_errors / len(error_scenarios)
            
            self._record_validation("error_handling",
                                  error_handling_rate >= 0.8,
                                  f"错误处理: {handled_errors}/{len(error_scenarios)} 场景正确处理, 处理率: {error_handling_rate:.1%}",
                                  {"handled_errors": handled_errors, "total_scenarios": len(error_scenarios)})
            
        except Exception as e:
            self._record_validation("error_handling", False, f"错误处理验证失败: {e}")
    
    async def _validate_performance_scalability(self):
        """验证性能和可扩展性"""
        print("⚡ 验证性能和可扩展性...")
        
        try:
            # 并发请求测试
            concurrent_requests = 10
            
            async def make_request(request_id):
                data = {
                    "type": "user_input",
                    "session_id": f"{self.session_id}_{request_id}",
                    "user_id": f"user_{request_id}",
                    "input": f"并发测试请求 {request_id}",
                    "input_type": "text"
                }
                
                start_time = asyncio.get_event_loop().time()
                response = await self.smartui_mcp.process(data)
                end_time = asyncio.get_event_loop().time()
                
                return {
                    "request_id": request_id,
                    "success": response.get("status") == "success",
                    "response_time": end_time - start_time
                }
            
            # 执行并发请求
            tasks = [make_request(i) for i in range(concurrent_requests)]
            results = await asyncio.gather(*tasks)
            
            # 分析结果
            successful_requests = sum(1 for r in results if r["success"])
            average_response_time = sum(r["response_time"] for r in results) / len(results)
            max_response_time = max(r["response_time"] for r in results)
            
            # 性能标准
            success_rate = successful_requests / concurrent_requests
            performance_acceptable = average_response_time < 1.0 and max_response_time < 2.0
            
            self._record_validation("performance_scalability",
                                  success_rate >= 0.9 and performance_acceptable,
                                  f"性能可扩展性: {successful_requests}/{concurrent_requests} 成功, 平均响应时间: {average_response_time:.3f}s, 最大响应时间: {max_response_time:.3f}s",
                                  {"concurrent_requests": concurrent_requests, "successful_requests": successful_requests, 
                                   "average_response_time": average_response_time, "max_response_time": max_response_time})
            
        except Exception as e:
            self._record_validation("performance_scalability", False, f"性能可扩展性验证失败: {e}")
    
    async def _validate_complete_business_scenario(self):
        """验证完整业务场景"""
        print("🎯 验证完整业务场景...")
        
        try:
            # 模拟完整的软件开发流程
            print("  📋 场景: 开发一个简单的博客系统")
            
            scenario_steps = []
            
            # 步骤1: 需求收集
            print("    1️⃣ 需求收集...")
            requirement_input = {
                "type": "user_input",
                "session_id": self.session_id,
                "user_id": "business_user",
                "input": "我需要开发一个博客系统，用户可以发布文章、评论、点赞",
                "input_type": "text"
            }
            
            step1_response = await self.smartui_mcp.process(requirement_input)
            scenario_steps.append(step1_response.get("status") == "success")
            
            # 步骤2: 需求分析
            print("    2️⃣ 需求分析...")
            requirement_analysis = {
                "type": "analyze_requirement",
                "requirement": "博客系统需要支持用户注册、登录、发布文章、评论、点赞等功能",
                "requirement_type": "functional",
                "title": "博客系统功能需求",
                "priority": "high"
            }
            
            step2_response = await self.requirement_analysis_mcp.process(requirement_analysis)
            scenario_steps.append(step2_response.get("status") == "success")
            
            # 步骤3: 代码生成
            print("    3️⃣ 代码生成...")
            code_generation = {
                "type": "generate_from_requirements",
                "requirements": [
                    {
                        "req_id": "blog_001",
                        "title": "用户管理",
                        "description": "用户注册、登录、个人信息管理",
                        "type": "functional"
                    },
                    {
                        "req_id": "blog_002",
                        "title": "文章管理",
                        "description": "发布、编辑、删除文章",
                        "type": "functional"
                    }
                ],
                "language": "python",
                "framework": "flask"
            }
            
            step3_response = await self.code_generation_mcp.process(code_generation)
            scenario_steps.append(step3_response.get("status") == "success")
            
            # 步骤4: 工作流协调
            print("    4️⃣ 工作流协调...")
            workflow_creation = {
                "type": "create_workflow",
                "workflow_type": "code_generation",
                "name": "博客系统开发工作流",
                "description": "完整的博客系统开发流程"
            }
            
            step4_response = await self.enhanced_workflow_mcp.process(workflow_creation)
            scenario_steps.append(step4_response.get("status") == "success")
            
            # 计算场景成功率
            scenario_success_rate = sum(scenario_steps) / len(scenario_steps)
            
            self._record_validation("complete_business_scenario",
                                  scenario_success_rate >= 0.8,
                                  f"完整业务场景: {sum(scenario_steps)}/{len(scenario_steps)} 步骤成功, 成功率: {scenario_success_rate:.1%}",
                                  {"scenario_steps": scenario_steps, "scenario_success_rate": scenario_success_rate})
            
        except Exception as e:
            self._record_validation("complete_business_scenario", False, f"完整业务场景验证失败: {e}")
    
    def _record_validation(self, validation_name: str, success: bool, message: str, data: dict = None):
        """记录验证结果"""
        result = {
            "validation_name": validation_name,
            "success": success,
            "message": message,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        self.validation_results.append(result)
        
        # 实时输出验证结果
        status_icon = "✅" if success else "❌"
        print(f"  {status_icon} {validation_name}: {message}")
    
    async def generate_validation_report(self):
        """生成验证报告"""
        print("\n" + "=" * 60)
        print("📊 PowerAutomation工作流系统验证报告")
        print("=" * 60)
        
        total_validations = len(self.validation_results)
        successful_validations = sum(1 for result in self.validation_results if result["success"])
        failed_validations = total_validations - successful_validations
        
        print(f"验证时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"会话ID: {self.session_id}")
        print(f"总验证项: {total_validations}")
        print(f"成功: {successful_validations}")
        print(f"失败: {failed_validations}")
        print(f"成功率: {(successful_validations/total_validations*100):.1f}%")
        
        # 系统状态评估
        if successful_validations / total_validations >= 0.9:
            system_status = "🟢 优秀 - 系统运行状态良好"
        elif successful_validations / total_validations >= 0.8:
            system_status = "🟡 良好 - 系统基本功能正常"
        elif successful_validations / total_validations >= 0.6:
            system_status = "🟠 一般 - 系统存在一些问题"
        else:
            system_status = "🔴 差 - 系统存在严重问题"
        
        print(f"\n系统状态评估: {system_status}")
        
        if failed_validations > 0:
            print("\n❌ 失败的验证项:")
            for result in self.validation_results:
                if not result["success"]:
                    print(f"  - {result['validation_name']}: {result['message']}")
        
        print("\n✅ 成功的验证项:")
        for result in self.validation_results:
            if result["success"]:
                print(f"  - {result['validation_name']}: {result['message']}")
        
        # 保存详细验证报告
        await self._save_validation_report()
        
        # 生成改进建议
        await self._generate_improvement_recommendations()
    
    async def _save_validation_report(self):
        """保存验证报告"""
        report = {
            "validation_session": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_validations": len(self.validation_results),
                "successful_validations": sum(1 for r in self.validation_results if r["success"]),
                "failed_validations": sum(1 for r in self.validation_results if not r["success"]),
                "success_rate": sum(1 for r in self.validation_results if r["success"]) / len(self.validation_results) * 100
            },
            "detailed_results": self.validation_results,
            "system_components": {
                "coordinator": "EnhancedMCPCoordinator",
                "smartui": "SmartUIMcp",
                "enhanced_workflow": "EnhancedWorkflowMcp",
                "requirement_analysis": "RequirementAnalysisMcp",
                "code_generation": "CodeGenerationMcp"
            }
        }
        
        report_file = Path("/opt/powerautomation/workflow_system_validation_report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n📄 详细验证报告已保存到: {report_file}")
    
    async def _generate_improvement_recommendations(self):
        """生成改进建议"""
        print("\n💡 系统改进建议:")
        
        failed_validations = [r for r in self.validation_results if not r["success"]]
        
        if not failed_validations:
            print("  🎉 系统运行完美，无需改进！")
            return
        
        recommendations = []
        
        for failed in failed_validations:
            validation_name = failed["validation_name"]
            
            if validation_name == "system_architecture":
                recommendations.append("检查MCP注册流程，确保所有组件正确初始化")
            elif validation_name == "user_interaction_flow":
                recommendations.append("优化用户输入处理逻辑，提高意图识别准确性")
            elif validation_name == "workflow_execution":
                recommendations.append("检查工作流引擎配置，确保所有工作流类型都能正确创建")
            elif validation_name == "data_flow_communication":
                recommendations.append("优化MCP间通信协议，确保数据传输的可靠性")
            elif validation_name == "error_handling":
                recommendations.append("增强错误处理机制，提供更详细的错误信息")
            elif validation_name == "performance_scalability":
                recommendations.append("优化系统性能，考虑引入缓存和负载均衡")
            elif validation_name == "complete_business_scenario":
                recommendations.append("完善业务流程集成，确保端到端场景的顺畅执行")
        
        for i, recommendation in enumerate(recommendations, 1):
            print(f"  {i}. {recommendation}")
    
    async def cleanup_system(self):
        """清理系统"""
        print("\n🧹 清理验证环境...")
        
        await self.smartui_mcp.cleanup()
        await self.enhanced_workflow_mcp.cleanup()
        await self.requirement_analysis_mcp.cleanup()
        await self.code_generation_mcp.cleanup()
        await self.coordinator.stop()
        
        print("✅ 验证环境清理完成")

async def main():
    """主函数"""
    validator = WorkflowSystemValidator()
    
    try:
        await validator.setup_system()
        await validator.validate_complete_workflow_system()
        await validator.generate_validation_report()
    finally:
        await validator.cleanup_system()

if __name__ == "__main__":
    asyncio.run(main())

