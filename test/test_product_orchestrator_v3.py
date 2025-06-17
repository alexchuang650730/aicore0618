#!/usr/bin/env python3
"""
Product Orchestrator V3 测试套件

遵循PowerAutomation统一测试框架规范
测试Product Orchestrator的四大核心能力：
1. 动态工作流生成能力
2. 并行调度支持多个MCP组件  
3. 智能依赖管理
4. 主动状态推送到SmartUI
"""

import asyncio
import unittest
import json
import time
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch
import sys
import os

# 添加项目路径
sys.path.append('/opt/powerautomation')

# 导入被测试的模块
from mcp.coordinator.workflow_collaboration.product_orchestrator_v3 import (
    ProductOrchestratorV3,
    DynamicWorkflowGenerator,
    ParallelExecutionScheduler,
    IntelligentDependencyManager,
    ActiveStatusPusher,
    WorkflowType,
    WorkflowStatus,
    DependencyType,
    WorkflowNode,
    DynamicWorkflow,
    StatusUpdate
)

class TestDynamicWorkflowGenerator(unittest.TestCase):
    """测试动态工作流生成器"""
    
    def setUp(self):
        self.generator = DynamicWorkflowGenerator()
    
    def test_workflow_template_loading(self):
        """测试工作流模板加载"""
        templates = self.generator.workflow_templates
        
        # 验证模板存在
        self.assertIn("software_development", templates)
        self.assertIn("quick_prototype", templates)
        self.assertIn("documentation_only", templates)
        
        # 验证软件开发模板包含所有六大工作流
        software_dev = templates["software_development"]
        self.assertEqual(len(software_dev), 6)
        self.assertIn(WorkflowType.REQUIREMENT_ANALYSIS, software_dev)
        self.assertIn(WorkflowType.CODE_IMPLEMENTATION, software_dev)
    
    def test_mcp_mapping_initialization(self):
        """测试MCP组件映射初始化"""
        mappings = self.generator.mcp_mappings
        
        # 验证所有工作流类型都有映射
        for workflow_type in WorkflowType:
            self.assertIn(workflow_type, mappings)
        
        # 验证需求分析映射
        req_mapping = mappings[WorkflowType.REQUIREMENT_ANALYSIS]
        self.assertEqual(req_mapping.primary_mcp, "requirement_analysis_mcp")
        self.assertTrue(req_mapping.tool_engine_required)
        self.assertTrue(req_mapping.search_fallback)
    
    async def test_generate_workflow_software_development(self):
        """测试生成软件开发工作流"""
        requirements = {
            "name": "Test Software Project",
            "description": "Create a web application with database",
            "complexity": "medium"
        }
        
        workflow = await self.generator.generate_workflow(requirements)
        
        # 验证工作流基本属性
        self.assertIsInstance(workflow, DynamicWorkflow)
        self.assertEqual(workflow.name, "Test Software Project")
        self.assertEqual(len(workflow.nodes), 6)  # 六大工作流
        
        # 验证节点类型
        node_types = [node.workflow_type for node in workflow.nodes]
        self.assertIn(WorkflowType.REQUIREMENT_ANALYSIS, node_types)
        self.assertIn(WorkflowType.CODE_IMPLEMENTATION, node_types)
        
        # 验证MCP组件分配
        first_node = workflow.nodes[0]
        self.assertIn("requirement_analysis_mcp", first_node.mcp_components)
        self.assertIn("unified_smart_tool_engine", first_node.mcp_components)
    
    async def test_generate_workflow_quick_prototype(self):
        """测试生成快速原型工作流"""
        requirements = {
            "name": "Quick Demo",
            "description": "Create a quick prototype for demo",
            "complexity": "simple"
        }
        
        workflow = await self.generator.generate_workflow(requirements)
        
        # 验证快速原型只有3个节点
        self.assertEqual(len(workflow.nodes), 3)
        
        # 验证节点类型
        node_types = [node.workflow_type for node in workflow.nodes]
        self.assertIn(WorkflowType.REQUIREMENT_ANALYSIS, node_types)
        self.assertIn(WorkflowType.CODE_IMPLEMENTATION, node_types)
        self.assertIn(WorkflowType.TEST_VERIFICATION, node_types)
    
    def test_requirement_analysis(self):
        """测试需求分析"""
        # 测试原型识别
        prototype_req = {"description": "quick prototype for demo"}
        template = self.generator._analyze_requirements(prototype_req)
        self.assertEqual(template, "quick_prototype")
        
        # 测试文档识别
        doc_req = {"description": "design architecture documentation"}
        template = self.generator._analyze_requirements(doc_req)
        self.assertEqual(template, "documentation_only")
        
        # 测试默认软件开发
        default_req = {"description": "build a web application"}
        template = self.generator._analyze_requirements(default_req)
        self.assertEqual(template, "software_development")
    
    def test_duration_estimation(self):
        """测试执行时间估算"""
        requirements = {"complexity": "simple"}
        
        # 测试简单复杂度
        duration = self.generator._estimate_node_duration(
            WorkflowType.CODE_IMPLEMENTATION, requirements
        )
        self.assertEqual(duration, 900)  # 1800 * 0.5
        
        # 测试复杂复杂度
        requirements["complexity"] = "complex"
        duration = self.generator._estimate_node_duration(
            WorkflowType.CODE_IMPLEMENTATION, requirements
        )
        self.assertEqual(duration, 3600)  # 1800 * 2.0

class TestParallelExecutionScheduler(unittest.TestCase):
    """测试并行执行调度器"""
    
    def setUp(self):
        self.scheduler = ParallelExecutionScheduler(max_parallel_tasks=2)
        self.mock_coordinator = AsyncMock()
    
    def test_scheduler_initialization(self):
        """测试调度器初始化"""
        self.assertEqual(self.scheduler.max_parallel_tasks, 2)
        self.assertIsNotNone(self.scheduler.executor)
        self.assertEqual(len(self.scheduler.running_tasks), 0)
    
    def test_create_execution_plan(self):
        """测试创建执行计划"""
        # 创建测试工作流
        nodes = [
            WorkflowNode(
                node_id="node_1",
                workflow_type=WorkflowType.REQUIREMENT_ANALYSIS,
                mcp_components=["requirement_analysis_mcp"],
                dependencies=[],
                dependency_type=DependencyType.SEQUENTIAL,
                estimated_duration=300,
                priority=10
            ),
            WorkflowNode(
                node_id="node_2",
                workflow_type=WorkflowType.ARCHITECTURE_DESIGN,
                mcp_components=["enhanced_workflow_mcp"],
                dependencies=["node_1"],
                dependency_type=DependencyType.SEQUENTIAL,
                estimated_duration=600,
                priority=9
            ),
            WorkflowNode(
                node_id="node_3",
                workflow_type=WorkflowType.CODE_IMPLEMENTATION,
                mcp_components=["code_generation_mcp"],
                dependencies=["node_2"],
                dependency_type=DependencyType.PARALLEL,
                estimated_duration=1800,
                priority=8
            )
        ]
        
        workflow = DynamicWorkflow(
            workflow_id="test_workflow",
            name="Test Workflow",
            description="Test workflow for execution plan",
            nodes=nodes,
            user_requirements={},
            generated_time=datetime.now(),
            estimated_total_duration=2700
        )
        
        execution_plan = self.scheduler._create_execution_plan(workflow)
        
        # 验证执行计划
        self.assertIn("level_0", execution_plan)
        self.assertIn("level_1", execution_plan)
        self.assertIn("level_2", execution_plan)
        
        # 验证第一层只有node_1
        self.assertEqual(execution_plan["level_0"], ["node_1"])
        
        # 验证第二层有node_2
        self.assertEqual(execution_plan["level_1"], ["node_2"])
        
        # 验证第三层有node_3
        self.assertEqual(execution_plan["level_2"], ["node_3"])
    
    async def test_execute_single_node_success(self):
        """测试单个节点执行成功"""
        node = WorkflowNode(
            node_id="test_node",
            workflow_type=WorkflowType.REQUIREMENT_ANALYSIS,
            mcp_components=["requirement_analysis_mcp"],
            dependencies=[],
            dependency_type=DependencyType.SEQUENTIAL,
            estimated_duration=300,
            priority=10
        )
        
        # 模拟成功响应
        mock_response = Mock()
        mock_response.status = "success"
        mock_response.response_data = {"result": "success"}
        
        self.mock_coordinator.route_request.return_value = mock_response
        
        result = await self.scheduler._execute_single_node(node, self.mock_coordinator)
        
        # 验证结果
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["data"], {"result": "success"})
        self.assertIn("execution_time", result)
        
        # 验证节点状态更新
        self.assertEqual(node.status, WorkflowStatus.COMPLETED)
        self.assertIsNotNone(node.start_time)
        self.assertIsNotNone(node.end_time)
    
    async def test_execute_single_node_failure(self):
        """测试单个节点执行失败"""
        node = WorkflowNode(
            node_id="test_node",
            workflow_type=WorkflowType.REQUIREMENT_ANALYSIS,
            mcp_components=["requirement_analysis_mcp"],
            dependencies=[],
            dependency_type=DependencyType.SEQUENTIAL,
            estimated_duration=300,
            priority=10
        )
        
        # 模拟异常
        self.mock_coordinator.route_request.side_effect = Exception("Test error")
        
        result = await self.scheduler._execute_single_node(node, self.mock_coordinator)
        
        # 验证错误结果
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["message"], "Test error")
        
        # 验证节点状态
        self.assertEqual(node.status, WorkflowStatus.FAILED)
        self.assertEqual(node.error_message, "Test error")

class TestIntelligentDependencyManager(unittest.TestCase):
    """测试智能依赖管理器"""
    
    def setUp(self):
        self.dependency_manager = IntelligentDependencyManager()
    
    def test_build_dependency_graph(self):
        """测试构建依赖图"""
        nodes = [
            WorkflowNode(
                node_id="node_1",
                workflow_type=WorkflowType.REQUIREMENT_ANALYSIS,
                mcp_components=["requirement_analysis_mcp"],
                dependencies=[],
                dependency_type=DependencyType.SEQUENTIAL,
                estimated_duration=300,
                priority=10
            ),
            WorkflowNode(
                node_id="node_2",
                workflow_type=WorkflowType.ARCHITECTURE_DESIGN,
                mcp_components=["enhanced_workflow_mcp"],
                dependencies=["node_1"],
                dependency_type=DependencyType.SEQUENTIAL,
                estimated_duration=600,
                priority=9
            )
        ]
        
        workflow = DynamicWorkflow(
            workflow_id="test_workflow",
            name="Test Workflow",
            description="Test workflow",
            nodes=nodes,
            user_requirements={},
            generated_time=datetime.now(),
            estimated_total_duration=900
        )
        
        graph = self.dependency_manager._build_dependency_graph(workflow)
        
        # 验证依赖图
        self.assertEqual(graph["node_1"], [])
        self.assertEqual(graph["node_2"], ["node_1"])
    
    def test_detect_cycles_no_cycle(self):
        """测试检测无循环依赖"""
        graph = {
            "node_1": [],
            "node_2": ["node_1"],
            "node_3": ["node_2"]
        }
        
        cycles = self.dependency_manager._detect_cycles(graph)
        self.assertEqual(len(cycles), 0)
    
    def test_detect_cycles_with_cycle(self):
        """测试检测循环依赖"""
        graph = {
            "node_1": ["node_3"],
            "node_2": ["node_1"],
            "node_3": ["node_2"]
        }
        
        cycles = self.dependency_manager._detect_cycles(graph)
        self.assertGreater(len(cycles), 0)
    
    def test_is_critical_dependency(self):
        """测试关键依赖判断"""
        # 需求分析是关键依赖
        req_node = WorkflowNode(
            node_id="req_node",
            workflow_type=WorkflowType.REQUIREMENT_ANALYSIS,
            mcp_components=["requirement_analysis_mcp"],
            dependencies=[],
            dependency_type=DependencyType.SEQUENTIAL,
            estimated_duration=300,
            priority=10
        )
        
        self.assertTrue(self.dependency_manager._is_critical_dependency(req_node))
        
        # 测试验证不是关键依赖
        test_node = WorkflowNode(
            node_id="test_node",
            workflow_type=WorkflowType.TEST_VERIFICATION,
            mcp_components=["test_manage_mcp"],
            dependencies=[],
            dependency_type=DependencyType.SEQUENTIAL,
            estimated_duration=900,
            priority=7
        )
        
        self.assertFalse(self.dependency_manager._is_critical_dependency(test_node))
    
    async def test_analyze_dependencies(self):
        """测试依赖分析"""
        nodes = [
            WorkflowNode(
                node_id="node_1",
                workflow_type=WorkflowType.REQUIREMENT_ANALYSIS,
                mcp_components=["requirement_analysis_mcp"],
                dependencies=[],
                dependency_type=DependencyType.SEQUENTIAL,
                estimated_duration=300,
                priority=10
            ),
            WorkflowNode(
                node_id="node_2",
                workflow_type=WorkflowType.ARCHITECTURE_DESIGN,
                mcp_components=["enhanced_workflow_mcp"],
                dependencies=["node_1"],
                dependency_type=DependencyType.SEQUENTIAL,
                estimated_duration=600,
                priority=9
            )
        ]
        
        workflow = DynamicWorkflow(
            workflow_id="test_workflow",
            name="Test Workflow",
            description="Test workflow",
            nodes=nodes,
            user_requirements={},
            generated_time=datetime.now(),
            estimated_total_duration=900
        )
        
        analysis = await self.dependency_manager.analyze_dependencies(workflow)
        
        # 验证分析结果
        self.assertIn("dependency_graph", analysis)
        self.assertIn("cycles", analysis)
        self.assertIn("optimized_dependencies", analysis)
        self.assertIn("critical_path", analysis)
        self.assertIn("analysis_time", analysis)

class TestActiveStatusPusher(unittest.TestCase):
    """测试主动状态推送器"""
    
    def setUp(self):
        self.status_pusher = ActiveStatusPusher("ws://localhost:5002")
    
    def test_status_pusher_initialization(self):
        """测试状态推送器初始化"""
        self.assertEqual(self.status_pusher.smartui_endpoint, "ws://localhost:5002")
        self.assertEqual(len(self.status_pusher.websocket_connections), 0)
        self.assertFalse(self.status_pusher.running)
    
    async def test_push_status_update(self):
        """测试推送状态更新"""
        update = StatusUpdate(
            update_id="test_update",
            workflow_id="test_workflow",
            node_id="test_node",
            status=WorkflowStatus.RUNNING,
            progress=0.5,
            message="Test message",
            timestamp=datetime.now()
        )
        
        # 推送状态更新
        await self.status_pusher.push_status_update(update)
        
        # 验证状态更新被添加到队列
        self.assertFalse(self.status_pusher.status_queue.empty())
        
        # 获取队列中的更新
        queued_update = await self.status_pusher.status_queue.get()
        self.assertEqual(queued_update.update_id, "test_update")
        self.assertEqual(queued_update.workflow_id, "test_workflow")

class TestProductOrchestratorV3Integration(unittest.TestCase):
    """测试Product Orchestrator V3集成"""
    
    def setUp(self):
        self.config = {
            "max_parallel_tasks": 2,
            "smartui_endpoint": "ws://localhost:5002"
        }
        self.orchestrator = ProductOrchestratorV3(self.config)
    
    def test_orchestrator_initialization(self):
        """测试编排器初始化"""
        self.assertIsNotNone(self.orchestrator.workflow_generator)
        self.assertIsNotNone(self.orchestrator.execution_scheduler)
        self.assertIsNotNone(self.orchestrator.dependency_manager)
        self.assertIsNotNone(self.orchestrator.status_pusher)
        
        # 验证配置
        self.assertEqual(
            self.orchestrator.execution_scheduler.max_parallel_tasks, 2
        )
    
    @patch('mcp.coordinator.workflow_collaboration.product_orchestrator_v3.EnhancedMCPCoordinator')
    @patch('mcp.coordinator.workflow_collaboration.product_orchestrator_v3.SmartRoutingSystem')
    @patch('mcp.coordinator.workflow_collaboration.product_orchestrator_v3.InteractionLogManager')
    async def test_create_and_execute_workflow_success(self, mock_log, mock_routing, mock_coordinator):
        """测试创建并执行工作流成功"""
        # 模拟MCP协调器响应
        mock_response = Mock()
        mock_response.status = "success"
        mock_response.response_data = {"result": "success"}
        mock_coordinator.return_value.route_request.return_value = mock_response
        
        # 模拟状态推送器
        self.orchestrator.status_pusher = AsyncMock()
        
        user_requirements = {
            "name": "Test Project",
            "description": "Create a quick prototype",
            "complexity": "simple"
        }
        
        result = await self.orchestrator.create_and_execute_workflow(user_requirements)
        
        # 验证结果
        self.assertIn("workflow_id", result)
        self.assertIn("status", result)
        self.assertIn("execution_result", result)
        self.assertIn("dependency_analysis", result)
        
        # 验证状态推送被调用
        self.orchestrator.status_pusher.push_status_update.assert_called()
    
    async def test_get_workflow_status(self):
        """测试获取工作流状态"""
        # 创建测试工作流
        workflow = DynamicWorkflow(
            workflow_id="test_workflow",
            name="Test Workflow",
            description="Test workflow",
            nodes=[],
            user_requirements={},
            generated_time=datetime.now(),
            estimated_total_duration=900
        )
        
        self.orchestrator.active_workflows["test_workflow"] = workflow
        
        status = await self.orchestrator.get_workflow_status("test_workflow")
        
        # 验证状态信息
        self.assertEqual(status["workflow_id"], "test_workflow")
        self.assertEqual(status["name"], "Test Workflow")
        self.assertIn("status", status)
        self.assertIn("progress", status)
    
    async def test_get_workflow_status_not_found(self):
        """测试获取不存在的工作流状态"""
        status = await self.orchestrator.get_workflow_status("nonexistent")
        
        self.assertEqual(status, {"error": "Workflow not found"})
    
    async def test_list_active_workflows(self):
        """测试列出活跃工作流"""
        # 添加测试工作流
        workflow1 = DynamicWorkflow(
            workflow_id="workflow_1",
            name="Workflow 1",
            description="Test workflow 1",
            nodes=[],
            user_requirements={},
            generated_time=datetime.now(),
            estimated_total_duration=900
        )
        
        workflow2 = DynamicWorkflow(
            workflow_id="workflow_2",
            name="Workflow 2",
            description="Test workflow 2",
            nodes=[],
            user_requirements={},
            generated_time=datetime.now(),
            estimated_total_duration=1200
        )
        
        self.orchestrator.active_workflows["workflow_1"] = workflow1
        self.orchestrator.active_workflows["workflow_2"] = workflow2
        
        workflows = await self.orchestrator.list_active_workflows()
        
        # 验证结果
        self.assertEqual(len(workflows), 2)
        workflow_ids = [w["workflow_id"] for w in workflows]
        self.assertIn("workflow_1", workflow_ids)
        self.assertIn("workflow_2", workflow_ids)

class TestProductOrchestratorV3Performance(unittest.TestCase):
    """测试Product Orchestrator V3性能"""
    
    def setUp(self):
        self.orchestrator = ProductOrchestratorV3()
    
    async def test_workflow_generation_performance(self):
        """测试工作流生成性能"""
        requirements = {
            "name": "Performance Test",
            "description": "Test workflow generation performance",
            "complexity": "medium"
        }
        
        start_time = time.time()
        workflow = await self.orchestrator.workflow_generator.generate_workflow(requirements)
        end_time = time.time()
        
        generation_time = end_time - start_time
        
        # 验证生成时间在合理范围内（小于1秒）
        self.assertLess(generation_time, 1.0)
        self.assertIsNotNone(workflow)
    
    async def test_dependency_analysis_performance(self):
        """测试依赖分析性能"""
        # 创建复杂工作流
        nodes = []
        for i in range(10):
            node = WorkflowNode(
                node_id=f"node_{i}",
                workflow_type=WorkflowType.CODE_IMPLEMENTATION,
                mcp_components=["code_generation_mcp"],
                dependencies=[f"node_{i-1}"] if i > 0 else [],
                dependency_type=DependencyType.SEQUENTIAL,
                estimated_duration=300,
                priority=10-i
            )
            nodes.append(node)
        
        workflow = DynamicWorkflow(
            workflow_id="performance_test",
            name="Performance Test Workflow",
            description="Test workflow for performance",
            nodes=nodes,
            user_requirements={},
            generated_time=datetime.now(),
            estimated_total_duration=3000
        )
        
        start_time = time.time()
        analysis = await self.orchestrator.dependency_manager.analyze_dependencies(workflow)
        end_time = time.time()
        
        analysis_time = end_time - start_time
        
        # 验证分析时间在合理范围内（小于2秒）
        self.assertLess(analysis_time, 2.0)
        self.assertIsNotNone(analysis)

if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 运行测试
    unittest.main(verbosity=2)

