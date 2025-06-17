#!/usr/bin/env python3
"""
端到端工作流通信测试
测试SmartUI MCP -> MCPCoordinator -> 各种工作流MCP的完整通信链路
"""

import asyncio
import json
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from mcp.enhanced_mcp_coordinator import EnhancedMCPCoordinator
from mcp.adapter.smartui_mcp.smartui_mcp import SmartUIMcp
from mcp.adapter.enhanced_workflow_mcp.enhanced_workflow_mcp import EnhancedWorkflowMcp
from mcp.adapter.requirement_analysis_mcp.requirement_analysis_mcp import RequirementAnalysisMcp
from mcp.adapter.code_generation_mcp.code_generation_mcp import CodeGenerationMcp

class EndToEndWorkflowTester:
    """端到端工作流测试器"""
    
    def __init__(self):
        self.coordinator = EnhancedMCPCoordinator()
        self.smartui_mcp = SmartUIMcp()
        self.enhanced_workflow_mcp = EnhancedWorkflowMcp()
        self.requirement_analysis_mcp = RequirementAnalysisMcp()
        self.code_generation_mcp = CodeGenerationMcp()
        
        self.test_results = []
        self.test_session_id = "test_session_001"
    
    async def setup(self):
        """设置测试环境"""
        print("🔧 设置测试环境...")
        
        # 启动协调器
        await self.coordinator.start()
        
        # 注册所有MCP
        await self.coordinator.register_mcp("smartui_mcp", self.smartui_mcp)
        await self.coordinator.register_mcp("enhanced_workflow_mcp", self.enhanced_workflow_mcp)
        await self.coordinator.register_mcp("requirement_analysis_mcp", self.requirement_analysis_mcp)
        await self.coordinator.register_mcp("code_generation_mcp", self.code_generation_mcp)
        
        print("✅ 测试环境设置完成")
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("\n🚀 开始端到端工作流通信测试")
        print("=" * 60)
        
        # 测试1: 基本通信测试
        await self.test_basic_communication()
        
        # 测试2: 用户输入处理测试
        await self.test_user_input_processing()
        
        # 测试3: 工作流创建测试
        await self.test_workflow_creation()
        
        # 测试4: 需求分析工作流测试
        await self.test_requirement_analysis_workflow()
        
        # 测试5: 代码生成工作流测试
        await self.test_code_generation_workflow()
        
        # 测试6: 完整端到端流程测试
        await self.test_complete_end_to_end_flow()
        
        # 输出测试结果
        await self.print_test_results()
    
    async def test_basic_communication(self):
        """测试基本通信"""
        print("\n📡 测试1: 基本通信测试")
        
        try:
            # 测试协调器状态
            coordinator_status = await self.coordinator.get_status()
            self.record_test_result("coordinator_status", True, "协调器状态正常", coordinator_status)
            
            # 测试MCP注册状态
            mcp_list = self.coordinator.mcp_registry.list_mcps()
            expected_mcps = ["smartui_mcp", "enhanced_workflow_mcp", "requirement_analysis_mcp", "code_generation_mcp"]
            
            all_registered = all(mcp in mcp_list for mcp in expected_mcps)
            self.record_test_result("mcp_registration", all_registered, 
                                  f"所有MCP已注册: {list(mcp_list.keys())}", mcp_list)
            
            # 测试健康检查
            health_status = await self.coordinator.mcp_registry.health_check_all()
            all_healthy = all(status["status"] == "healthy" for status in health_status.values())
            self.record_test_result("health_check", all_healthy, "所有MCP健康状态正常", health_status)
            
        except Exception as e:
            self.record_test_result("basic_communication", False, f"基本通信测试失败: {e}")
    
    async def test_user_input_processing(self):
        """测试用户输入处理"""
        print("\n👤 测试2: 用户输入处理测试")
        
        try:
            # 模拟用户输入
            user_input_data = {
                "type": "user_input",
                "session_id": self.test_session_id,
                "user_id": "test_user",
                "input": "我想创建一个需求分析工作流",
                "input_type": "text"
            }
            
            # 通过SmartUI MCP处理用户输入
            response = await self.smartui_mcp.process(user_input_data)
            
            success = response.get("status") == "success"
            self.record_test_result("user_input_processing", success, 
                                  "用户输入处理成功", response)
            
            # 验证意图识别
            intent = response.get("intent")
            expected_intent = "requirement_analysis"
            intent_correct = intent == expected_intent
            self.record_test_result("intent_recognition", intent_correct,
                                  f"意图识别正确: {intent}", {"detected_intent": intent})
            
        except Exception as e:
            self.record_test_result("user_input_processing", False, f"用户输入处理测试失败: {e}")
    
    async def test_workflow_creation(self):
        """测试工作流创建"""
        print("\n⚙️ 测试3: 工作流创建测试")
        
        try:
            # 创建工作流请求
            workflow_request_data = {
                "type": "workflow_request",
                "session_id": self.test_session_id,
                "workflow_type": "requirement_analysis",
                "workflow_name": "测试需求分析工作流",
                "description": "用于测试的需求分析工作流"
            }
            
            # 通过SmartUI MCP创建工作流请求
            smartui_response = await self.smartui_mcp.process(workflow_request_data)
            
            success = smartui_response.get("status") == "success"
            self.record_test_result("workflow_request_creation", success,
                                  "工作流请求创建成功", smartui_response)
            
            # 获取协调器请求
            coordinator_request = smartui_response.get("coordinator_request")
            if coordinator_request:
                # 通过协调器处理请求
                coordinator_response = await self.coordinator.handle_smartui_request(coordinator_request)
                
                coord_success = coordinator_response.get("status") == "success"
                self.record_test_result("coordinator_routing", coord_success,
                                      "协调器路由成功", coordinator_response)
            
        except Exception as e:
            self.record_test_result("workflow_creation", False, f"工作流创建测试失败: {e}")
    
    async def test_requirement_analysis_workflow(self):
        """测试需求分析工作流"""
        print("\n📋 测试4: 需求分析工作流测试")
        
        try:
            # 创建需求分析请求
            requirement_data = {
                "type": "analyze_requirement",
                "requirement": "系统需要提供用户登录功能，支持用户名密码登录和第三方登录",
                "requirement_type": "functional",
                "title": "用户登录功能",
                "priority": "high",
                "session_id": self.test_session_id
            }
            
            # 直接测试需求分析MCP
            analysis_response = await self.requirement_analysis_mcp.process(requirement_data)
            
            success = analysis_response.get("status") == "success"
            self.record_test_result("requirement_analysis", success,
                                  "需求分析处理成功", analysis_response)
            
            # 验证分析结果
            analysis_result = analysis_response.get("analysis_result")
            if analysis_result:
                quality_score = analysis_result.get("quality_score", 0)
                quality_good = quality_score > 70
                self.record_test_result("requirement_quality", quality_good,
                                      f"需求质量分数: {quality_score}", analysis_result)
            
        except Exception as e:
            self.record_test_result("requirement_analysis_workflow", False, 
                                  f"需求分析工作流测试失败: {e}")
    
    async def test_code_generation_workflow(self):
        """测试代码生成工作流"""
        print("\n💻 测试5: 代码生成工作流测试")
        
        try:
            # 创建代码生成请求
            code_gen_data = {
                "type": "generate_code",
                "code_type": "api",
                "language": "python",
                "framework": "flask",
                "specifications": {
                    "endpoint": "login",
                    "method": "POST",
                    "function_name": "user_login",
                    "description": "用户登录API端点"
                }
            }
            
            # 直接测试代码生成MCP
            generation_response = await self.code_generation_mcp.process(code_gen_data)
            
            success = generation_response.get("status") == "success"
            self.record_test_result("code_generation", success,
                                  "代码生成处理成功", generation_response)
            
            # 验证生成的代码
            generated_code = generation_response.get("generated_code")
            if generated_code:
                code_has_content = len(generated_code.strip()) > 100
                self.record_test_result("generated_code_quality", code_has_content,
                                      "生成的代码有实质内容", {"code_length": len(generated_code)})
            
        except Exception as e:
            self.record_test_result("code_generation_workflow", False,
                                  f"代码生成工作流测试失败: {e}")
    
    async def test_complete_end_to_end_flow(self):
        """测试完整端到端流程"""
        print("\n🔄 测试6: 完整端到端流程测试")
        
        try:
            # 步骤1: 用户输入需求
            user_input = {
                "type": "user_input",
                "session_id": self.test_session_id,
                "user_id": "test_user",
                "input": "我需要创建一个用户管理系统，包括用户注册、登录、个人信息管理功能",
                "input_type": "text"
            }
            
            smartui_response = await self.smartui_mcp.process(user_input)
            step1_success = smartui_response.get("status") == "success"
            
            # 步骤2: 创建需求分析工作流
            workflow_request = {
                "type": "workflow_request",
                "session_id": self.test_session_id,
                "workflow_type": "requirement_analysis",
                "workflow_name": "用户管理系统需求分析",
                "description": "分析用户管理系统的详细需求"
            }
            
            workflow_response = await self.smartui_mcp.process(workflow_request)
            step2_success = workflow_response.get("status") == "success"
            
            # 步骤3: 通过协调器路由到需求分析MCP
            if step2_success:
                coordinator_request = workflow_response.get("coordinator_request")
                if coordinator_request:
                    coord_response = await self.coordinator.handle_smartui_request(coordinator_request)
                    step3_success = coord_response.get("status") == "success"
                else:
                    step3_success = False
            else:
                step3_success = False
            
            # 步骤4: 执行需求分析
            requirement_analysis = {
                "type": "analyze_requirement",
                "requirement": "用户管理系统需要支持用户注册、登录、个人信息管理等功能",
                "requirement_type": "functional",
                "title": "用户管理系统",
                "priority": "high"
            }
            
            analysis_response = await self.requirement_analysis_mcp.process(requirement_analysis)
            step4_success = analysis_response.get("status") == "success"
            
            # 步骤5: 基于需求生成代码
            if step4_success:
                code_generation = {
                    "type": "generate_from_requirements",
                    "requirements": [
                        {
                            "req_id": "req_001",
                            "title": "用户注册",
                            "description": "用户可以通过邮箱和密码注册账户",
                            "type": "functional"
                        },
                        {
                            "req_id": "req_002", 
                            "title": "用户登录",
                            "description": "用户可以使用邮箱和密码登录系统",
                            "type": "functional"
                        }
                    ],
                    "language": "python",
                    "framework": "flask"
                }
                
                code_response = await self.code_generation_mcp.process(code_generation)
                step5_success = code_response.get("status") == "success"
            else:
                step5_success = False
            
            # 记录完整流程结果
            all_steps_success = all([step1_success, step2_success, step3_success, step4_success, step5_success])
            
            self.record_test_result("complete_end_to_end_flow", all_steps_success,
                                  f"完整端到端流程测试: 步骤成功率 {sum([step1_success, step2_success, step3_success, step4_success, step5_success])}/5",
                                  {
                                      "step1_user_input": step1_success,
                                      "step2_workflow_creation": step2_success,
                                      "step3_coordinator_routing": step3_success,
                                      "step4_requirement_analysis": step4_success,
                                      "step5_code_generation": step5_success
                                  })
            
        except Exception as e:
            self.record_test_result("complete_end_to_end_flow", False,
                                  f"完整端到端流程测试失败: {e}")
    
    def record_test_result(self, test_name: str, success: bool, message: str, data: dict = None):
        """记录测试结果"""
        result = {
            "test_name": test_name,
            "success": success,
            "message": message,
            "data": data,
            "timestamp": asyncio.get_event_loop().time()
        }
        self.test_results.append(result)
        
        # 实时输出测试结果
        status_icon = "✅" if success else "❌"
        print(f"  {status_icon} {test_name}: {message}")
    
    async def print_test_results(self):
        """输出测试结果总结"""
        print("\n" + "=" * 60)
        print("📊 测试结果总结")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - successful_tests
        
        print(f"总测试数: {total_tests}")
        print(f"成功: {successful_tests}")
        print(f"失败: {failed_tests}")
        print(f"成功率: {(successful_tests/total_tests*100):.1f}%")
        
        if failed_tests > 0:
            print("\n❌ 失败的测试:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test_name']}: {result['message']}")
        
        print("\n✅ 成功的测试:")
        for result in self.test_results:
            if result["success"]:
                print(f"  - {result['test_name']}: {result['message']}")
        
        # 保存详细测试报告
        await self.save_test_report()
    
    async def save_test_report(self):
        """保存测试报告"""
        report = {
            "test_session": self.test_session_id,
            "timestamp": asyncio.get_event_loop().time(),
            "summary": {
                "total_tests": len(self.test_results),
                "successful_tests": sum(1 for r in self.test_results if r["success"]),
                "failed_tests": sum(1 for r in self.test_results if not r["success"]),
                "success_rate": sum(1 for r in self.test_results if r["success"]) / len(self.test_results) * 100
            },
            "detailed_results": self.test_results
        }
        
        report_file = Path("/opt/powerautomation/end_to_end_test_report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"\n📄 详细测试报告已保存到: {report_file}")
    
    async def cleanup(self):
        """清理测试环境"""
        print("\n🧹 清理测试环境...")
        
        await self.smartui_mcp.cleanup()
        await self.enhanced_workflow_mcp.cleanup()
        await self.requirement_analysis_mcp.cleanup()
        await self.code_generation_mcp.cleanup()
        await self.coordinator.stop()
        
        print("✅ 测试环境清理完成")

async def main():
    """主函数"""
    tester = EndToEndWorkflowTester()
    
    try:
        await tester.setup()
        await tester.run_all_tests()
    finally:
        await tester.cleanup()

if __name__ == "__main__":
    asyncio.run(main())

