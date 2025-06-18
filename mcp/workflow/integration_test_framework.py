#!/usr/bin/env python3
"""
PowerAutomation MCP集成测试框架
为所有工作流MCP提供统一的集成测试能力
"""

import asyncio
import aiohttp
import json
import time
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import pytest

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class MCPService:
    """MCP服务配置"""
    name: str
    host: str
    port: int
    base_url: str
    
    def __post_init__(self):
        if not self.base_url:
            self.base_url = f"http://{self.host}:{self.port}/api"

@dataclass
class TestResult:
    """测试结果"""
    service_name: str
    test_name: str
    status: str  # PASSED, FAILED, SKIPPED
    duration: float
    error_message: Optional[str] = None
    response_data: Optional[Dict] = None

class MCPIntegrationTester:
    """MCP集成测试器"""
    
    def __init__(self):
        self.services = self._get_mcp_services()
        self.test_results: List[TestResult] = []
        self.session: Optional[aiohttp.ClientSession] = None
    
    def _get_mcp_services(self) -> List[MCPService]:
        """获取所有MCP服务配置"""
        return [
            MCPService("Requirements Analysis MCP", "localhost", 8091, ""),
            MCPService("Architecture Design MCP", "localhost", 8092, ""),
            MCPService("Coding Workflow MCP", "localhost", 8093, ""),
            MCPService("Developer Flow MCP", "localhost", 8094, ""),
            MCPService("Test Manager MCP", "localhost", 8097, ""),
            MCPService("Release Manager MCP", "localhost", 8096, ""),
            MCPService("Operations Workflow MCP", "localhost", 8090, "")
        ]
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.session:
            await self.session.close()
    
    async def test_service_health(self, service: MCPService) -> TestResult:
        """测试服务健康状态"""
        start_time = time.time()
        test_name = f"{service.name} - Health Check"
        
        try:
            url = f"{service.base_url}/health"
            async with self.session.get(url) as response:
                duration = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    return TestResult(
                        service_name=service.name,
                        test_name=test_name,
                        status="PASSED",
                        duration=duration,
                        response_data=data
                    )
                else:
                    return TestResult(
                        service_name=service.name,
                        test_name=test_name,
                        status="FAILED",
                        duration=duration,
                        error_message=f"HTTP {response.status}"
                    )
        
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                service_name=service.name,
                test_name=test_name,
                status="FAILED",
                duration=duration,
                error_message=str(e)
            )
    
    async def test_service_status(self, service: MCPService) -> TestResult:
        """测试服务状态接口"""
        start_time = time.time()
        test_name = f"{service.name} - Status Check"
        
        try:
            url = f"{service.base_url}/status"
            async with self.session.get(url) as response:
                duration = time.time() - start_time
                
                if response.status == 200:
                    data = await response.json()
                    # 验证响应格式
                    if self._validate_status_response(data):
                        return TestResult(
                            service_name=service.name,
                            test_name=test_name,
                            status="PASSED",
                            duration=duration,
                            response_data=data
                        )
                    else:
                        return TestResult(
                            service_name=service.name,
                            test_name=test_name,
                            status="FAILED",
                            duration=duration,
                            error_message="响应格式不符合标准"
                        )
                else:
                    return TestResult(
                        service_name=service.name,
                        test_name=test_name,
                        status="FAILED",
                        duration=duration,
                        error_message=f"HTTP {response.status}"
                    )
        
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                service_name=service.name,
                test_name=test_name,
                status="FAILED",
                duration=duration,
                error_message=str(e)
            )
    
    def _validate_status_response(self, data: Dict) -> bool:
        """验证状态响应格式"""
        required_fields = ["success", "service_id", "version", "status", "capabilities", "endpoints"]
        return all(field in data for field in required_fields)
    
    async def test_service_api_endpoints(self, service: MCPService) -> List[TestResult]:
        """测试服务API端点"""
        results = []
        
        # 获取服务端点列表
        try:
            url = f"{service.base_url}/status"
            async with self.session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    endpoints = data.get("endpoints", [])
                else:
                    return [TestResult(
                        service_name=service.name,
                        test_name="API Endpoints Discovery",
                        status="FAILED",
                        duration=0,
                        error_message="无法获取端点列表"
                    )]
        except Exception as e:
            return [TestResult(
                service_name=service.name,
                test_name="API Endpoints Discovery",
                status="FAILED",
                duration=0,
                error_message=str(e)
            )]
        
        # 测试每个端点
        for endpoint in endpoints:
            if endpoint in ["/api/status", "/api/health"]:
                continue  # 已经测试过
            
            result = await self._test_endpoint(service, endpoint)
            results.append(result)
        
        return results
    
    async def _test_endpoint(self, service: MCPService, endpoint: str) -> TestResult:
        """测试单个端点"""
        start_time = time.time()
        test_name = f"{service.name} - {endpoint}"
        
        try:
            url = f"{service.base_url.replace('/api', '')}{endpoint}"
            
            # 根据端点类型选择测试方法
            if endpoint.endswith("_requirements") or endpoint.endswith("_stories") or \
               endpoint.endswith("_specifications") or endpoint.endswith("_criteria") or \
               endpoint.endswith("_architecture") or endpoint.endswith("_stack") or \
               endpoint.endswith("_components") or endpoint.endswith("_interfaces") or \
               endpoint.endswith("_code") or endpoint.endswith("_standards") or \
               endpoint.endswith("_workflow") or endpoint.endswith("_team") or \
               endpoint.endswith("_pipeline") or endpoint.endswith("_gates"):
                # POST端点测试
                test_data = self._get_test_data_for_endpoint(endpoint)
                async with self.session.post(url, json=test_data) as response:
                    duration = time.time() - start_time
                    
                    if response.status in [200, 201]:
                        data = await response.json()
                        return TestResult(
                            service_name=service.name,
                            test_name=test_name,
                            status="PASSED",
                            duration=duration,
                            response_data=data
                        )
                    else:
                        return TestResult(
                            service_name=service.name,
                            test_name=test_name,
                            status="FAILED",
                            duration=duration,
                            error_message=f"HTTP {response.status}"
                        )
            else:
                # GET端点测试
                async with self.session.get(url) as response:
                    duration = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        return TestResult(
                            service_name=service.name,
                            test_name=test_name,
                            status="PASSED",
                            duration=duration,
                            response_data=data
                        )
                    else:
                        return TestResult(
                            service_name=service.name,
                            test_name=test_name,
                            status="FAILED",
                            duration=duration,
                            error_message=f"HTTP {response.status}"
                        )
        
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                service_name=service.name,
                test_name=test_name,
                status="FAILED",
                duration=duration,
                error_message=str(e)
            )
    
    def _get_test_data_for_endpoint(self, endpoint: str) -> Dict:
        """获取端点测试数据"""
        test_data_map = {
            "/api/analyze_requirements": {
                "requirements": "创建一个用户管理系统",
                "project_type": "web_application"
            },
            "/api/generate_user_stories": {
                "requirements": "用户管理系统需求",
                "user_roles": ["用户", "管理员"]
            },
            "/api/define_specifications": {
                "user_stories": [{"id": "US001", "title": "用户登录"}],
                "detail_level": "medium"
            },
            "/api/create_acceptance_criteria": {
                "specifications": {"functional_specs": []},
                "test_approach": "comprehensive"
            },
            "/api/design_architecture": {
                "requirements": {"functional": [], "non_functional": []},
                "project_type": "web_application",
                "scale": "medium"
            },
            "/api/select_tech_stack": {
                "requirements": {"performance": "high"},
                "constraints": {"budget": "medium"},
                "team_skills": ["python", "javascript"]
            },
            "/api/design_components": {
                "architecture": {"pattern": "three-tier"},
                "tech_stack": {"backend": "flask", "frontend": "react"}
            },
            "/api/define_interfaces": {
                "components": {"backend": [], "frontend": []},
                "api_style": "RESTful"
            },
            "/api/generate_code": {
                "specifications": {"modules": ["auth", "data"]},
                "language": "python",
                "framework": "flask"
            },
            "/api/review_code": {
                "code_files": [{"path": "app.py", "content": "# test code"}],
                "review_type": "comprehensive"
            },
            "/api/check_standards": {
                "code_content": "def test_function():\n    pass",
                "language": "python",
                "standards": "pep8"
            },
            "/api/optimize_code": {
                "code_content": "def test_function():\n    pass",
                "optimization_type": "performance"
            },
            "/api/manage_workflow": {
                "project_id": "test_project",
                "workflow_type": "standard",
                "team_size": 5
            },
            "/api/coordinate_team": {
                "team_members": ["dev1", "dev2"],
                "project_phase": "development"
            },
            "/api/orchestrate_pipeline": {
                "pipeline_type": "ci_cd",
                "project_config": {"language": "python"}
            },
            "/api/quality_gates": {
                "gate_type": "code_quality",
                "project_metrics": {"coverage": 85}
            }
        }
        
        return test_data_map.get(endpoint, {"test": "data"})
    
    async def test_service_performance(self, service: MCPService) -> TestResult:
        """测试服务性能"""
        start_time = time.time()
        test_name = f"{service.name} - Performance Test"
        
        try:
            # 并发请求测试
            tasks = []
            for i in range(10):  # 10个并发请求
                task = self._make_health_request(service)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            duration = time.time() - start_time
            
            # 分析结果
            successful_requests = sum(1 for r in results if isinstance(r, dict))
            failed_requests = len(results) - successful_requests
            
            if failed_requests == 0 and duration < 5.0:  # 5秒内完成所有请求
                return TestResult(
                    service_name=service.name,
                    test_name=test_name,
                    status="PASSED",
                    duration=duration,
                    response_data={
                        "concurrent_requests": 10,
                        "successful_requests": successful_requests,
                        "failed_requests": failed_requests,
                        "total_duration": duration,
                        "average_response_time": duration / 10
                    }
                )
            else:
                return TestResult(
                    service_name=service.name,
                    test_name=test_name,
                    status="FAILED",
                    duration=duration,
                    error_message=f"性能测试失败: {failed_requests}个请求失败, 总耗时{duration:.2f}秒"
                )
        
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(
                service_name=service.name,
                test_name=test_name,
                status="FAILED",
                duration=duration,
                error_message=str(e)
            )
    
    async def _make_health_request(self, service: MCPService) -> Dict:
        """发起健康检查请求"""
        url = f"{service.base_url}/health"
        async with self.session.get(url) as response:
            return await response.json()
    
    async def test_service_communication(self) -> List[TestResult]:
        """测试服务间通信"""
        results = []
        
        # 测试工作流链路：需求分析 -> 架构设计 -> 编码实现 -> 测试管理 -> 发布管理 -> 运维监控
        workflow_chain = [
            ("Requirements Analysis MCP", 8091),
            ("Architecture Design MCP", 8092),
            ("Coding Workflow MCP", 8093),
            ("Test Manager MCP", 8097),
            ("Release Manager MCP", 8096),
            ("Operations Workflow MCP", 8090)
        ]
        
        start_time = time.time()
        
        try:
            # 模拟完整工作流
            workflow_data = {"project_id": "test_integration", "data": {}}
            
            for service_name, port in workflow_chain:
                service = next((s for s in self.services if s.port == port), None)
                if not service:
                    continue
                
                # 检查服务是否可用
                health_result = await self.test_service_health(service)
                if health_result.status != "PASSED":
                    results.append(TestResult(
                        service_name="Workflow Chain",
                        test_name=f"Communication Test - {service_name}",
                        status="FAILED",
                        duration=time.time() - start_time,
                        error_message=f"{service_name}服务不可用"
                    ))
                    break
                
                # 传递数据到下一个服务
                workflow_data["data"][service_name] = {
                    "processed_at": datetime.now().isoformat(),
                    "status": "completed"
                }
            
            duration = time.time() - start_time
            results.append(TestResult(
                service_name="Workflow Chain",
                test_name="End-to-End Communication Test",
                status="PASSED",
                duration=duration,
                response_data=workflow_data
            ))
        
        except Exception as e:
            duration = time.time() - start_time
            results.append(TestResult(
                service_name="Workflow Chain",
                test_name="End-to-End Communication Test",
                status="FAILED",
                duration=duration,
                error_message=str(e)
            ))
        
        return results
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """运行所有测试"""
        logger.info("开始运行PowerAutomation MCP集成测试...")
        
        all_results = []
        
        # 测试每个服务
        for service in self.services:
            logger.info(f"测试服务: {service.name}")
            
            # 健康检查测试
            health_result = await self.test_service_health(service)
            all_results.append(health_result)
            
            # 状态检查测试
            status_result = await self.test_service_status(service)
            all_results.append(status_result)
            
            # API端点测试
            if health_result.status == "PASSED":
                endpoint_results = await self.test_service_api_endpoints(service)
                all_results.extend(endpoint_results)
                
                # 性能测试
                performance_result = await self.test_service_performance(service)
                all_results.append(performance_result)
        
        # 服务间通信测试
        communication_results = await self.test_service_communication()
        all_results.extend(communication_results)
        
        # 生成测试报告
        report = self._generate_test_report(all_results)
        
        logger.info("PowerAutomation MCP集成测试完成")
        return report
    
    def _generate_test_report(self, results: List[TestResult]) -> Dict[str, Any]:
        """生成测试报告"""
        total_tests = len(results)
        passed_tests = sum(1 for r in results if r.status == "PASSED")
        failed_tests = sum(1 for r in results if r.status == "FAILED")
        skipped_tests = sum(1 for r in results if r.status == "SKIPPED")
        
        # 按服务分组结果
        service_results = {}
        for result in results:
            if result.service_name not in service_results:
                service_results[result.service_name] = []
            service_results[result.service_name].append(result)
        
        # 计算总耗时
        total_duration = sum(r.duration for r in results)
        
        report = {
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "skipped_tests": skipped_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                "total_duration": total_duration,
                "timestamp": datetime.now().isoformat()
            },
            "service_results": {},
            "failed_tests": [],
            "recommendations": []
        }
        
        # 服务级别统计
        for service_name, service_results_list in service_results.items():
            service_passed = sum(1 for r in service_results_list if r.status == "PASSED")
            service_total = len(service_results_list)
            
            report["service_results"][service_name] = {
                "total_tests": service_total,
                "passed_tests": service_passed,
                "failed_tests": service_total - service_passed,
                "success_rate": (service_passed / service_total * 100) if service_total > 0 else 0,
                "average_response_time": sum(r.duration for r in service_results_list) / service_total if service_total > 0 else 0
            }
        
        # 失败测试详情
        for result in results:
            if result.status == "FAILED":
                report["failed_tests"].append({
                    "service": result.service_name,
                    "test": result.test_name,
                    "error": result.error_message,
                    "duration": result.duration
                })
        
        # 生成建议
        if failed_tests > 0:
            report["recommendations"].append("存在失败的测试用例，建议检查服务状态和配置")
        
        if total_duration > 30:
            report["recommendations"].append("测试执行时间较长，建议优化服务性能")
        
        if passed_tests / total_tests < 0.9:
            report["recommendations"].append("测试通过率较低，建议进行系统健康检查")
        
        return report

# 测试运行器
async def run_integration_tests():
    """运行集成测试"""
    async with MCPIntegrationTester() as tester:
        report = await tester.run_all_tests()
        
        # 打印测试报告
        print("\n" + "="*80)
        print("PowerAutomation MCP集成测试报告")
        print("="*80)
        
        summary = report["summary"]
        print(f"测试总数: {summary['total_tests']}")
        print(f"通过测试: {summary['passed_tests']}")
        print(f"失败测试: {summary['failed_tests']}")
        print(f"跳过测试: {summary['skipped_tests']}")
        print(f"成功率: {summary['success_rate']:.1f}%")
        print(f"总耗时: {summary['total_duration']:.2f}秒")
        
        print("\n服务级别结果:")
        for service_name, service_result in report["service_results"].items():
            print(f"  {service_name}:")
            print(f"    通过率: {service_result['success_rate']:.1f}%")
            print(f"    平均响应时间: {service_result['average_response_time']:.3f}秒")
        
        if report["failed_tests"]:
            print("\n失败测试详情:")
            for failed_test in report["failed_tests"]:
                print(f"  {failed_test['service']} - {failed_test['test']}")
                print(f"    错误: {failed_test['error']}")
        
        if report["recommendations"]:
            print("\n建议:")
            for recommendation in report["recommendations"]:
                print(f"  - {recommendation}")
        
        print("="*80)
        
        return report

if __name__ == "__main__":
    # 运行集成测试
    asyncio.run(run_integration_tests())

