#!/usr/bin/env python3
"""
SmartUI Enhanced - 主服务器
整合所有组件，提供统一的API接口和Web界面
"""

import asyncio
import json
import time
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string, send_from_directory
from flask_cors import CORS
import threading
import os
import sys

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api_state_manager import APIStateManager, APIRoute
from user_analyzer import UserAnalyzer, UserProfile, InteractionPattern
from decision_engine import DecisionEngine, DecisionContext, DecisionResult
from ui_generator import UIGenerator, UIRequirements, ComponentConfig, ComponentType, LayoutType, ThemeType
from mcp_integration import MCPCoordinatorClient, MCPCollaborator, WorkflowDriver, CollaborationType

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SmartUIEnhancedServer:
    """SmartUI Enhanced 主服务器"""
    
    def __init__(self, host="0.0.0.0", port=5002):
        self.host = host
        self.port = port
        self.app = Flask(__name__)
        CORS(self.app)  # 启用CORS
        
        # 初始化核心组件
        self.api_state_manager = APIStateManager()
        self.user_analyzer = UserAnalyzer()
        self.decision_engine = DecisionEngine()
        self.ui_generator = UIGenerator()
        
        # 初始化MCP集成组件
        self.coordinator_client = MCPCoordinatorClient()
        self.mcp_collaborator = MCPCollaborator(self.coordinator_client)
        self.workflow_driver = WorkflowDriver(self.mcp_collaborator)
        
        # 服务器状态
        self.server_start_time = datetime.now()
        self.request_count = 0
        self.active_sessions = {}
        
        # 注册路由
        self._register_routes()
        
        # 注册到MCP协调器
        asyncio.create_task(self._register_to_coordinator())
    
    async def _register_to_coordinator(self):
        """注册到MCP协调器"""
        try:
            from mcp_integration import MCPInfo, MCPStatus
            
            mcp_info = MCPInfo(
                mcp_id="smartui_enhanced",
                name="SmartUI Enhanced MCP",
                endpoint=f"http://{self.host}:{self.port}",
                capabilities=[
                    "ui_generation",
                    "user_analysis", 
                    "decision_making",
                    "workflow_coordination",
                    "api_state_management",
                    "real_time_adaptation"
                ],
                status=MCPStatus.ONLINE,
                last_heartbeat=datetime.now(),
                response_time=0.0,
                error_count=0,
                metadata={
                    "version": "1.0.0",
                    "description": "智能交互界面生成和管理系统",
                    "supported_themes": ["light", "dark", "auto", "high_contrast"],
                    "supported_layouts": ["grid", "flexbox", "sidebar", "dashboard"]
                }
            )
            
            success = await self.coordinator_client.register_mcp(mcp_info)
            if success:
                logger.info("成功注册到MCP协调器")
            else:
                logger.warning("注册到MCP协调器失败")
                
        except Exception as e:
            logger.error(f"注册到MCP协调器异常: {e}")
    
    def _register_routes(self):
        """注册API路由"""
        
        # 健康检查
        @self.app.route('/health', methods=['GET'])
        def health_check():
            return jsonify({
                "status": "healthy",
                "server": "SmartUI Enhanced",
                "version": "1.0.0",
                "uptime": int((datetime.now() - self.server_start_time).total_seconds()),
                "request_count": self.request_count
            })
        
        # 主页面
        @self.app.route('/', methods=['GET'])
        def index():
            return render_template_string(self._get_main_page_template())
        
        # 用户分析API
        @self.app.route('/api/user/analyze', methods=['POST'])
        def analyze_user():
            self.request_count += 1
            try:
                data = request.get_json()
                user_id = data.get('user_id', 'anonymous')
                interaction_data = data.get('interaction_data', {})
                
                # 分析用户行为
                analysis_result = asyncio.run(
                    self.user_analyzer.analyze_user_behavior(user_id, interaction_data)
                )
                
                return jsonify({
                    "success": True,
                    "user_id": user_id,
                    "analysis": analysis_result,
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"用户分析失败: {e}")
                return jsonify({"success": False, "error": str(e)}), 500
        
        # 决策引擎API
        @self.app.route('/api/decision/make', methods=['POST'])
        def make_decision():
            self.request_count += 1
            try:
                data = request.get_json()
                
                # 构建决策上下文
                context = DecisionContext(
                    user_id=data.get('user_id', 'anonymous'),
                    current_state=data.get('current_state', {}),
                    user_input=data.get('user_input', {}),
                    environment=data.get('environment', {}),
                    constraints=data.get('constraints', {}),
                    goals=data.get('goals', [])
                )
                
                # 执行决策
                decision_result = asyncio.run(
                    self.decision_engine.make_decision(context)
                )
                
                return jsonify({
                    "success": True,
                    "decision": {
                        "action": decision_result.action,
                        "confidence": decision_result.confidence,
                        "reasoning": decision_result.reasoning,
                        "alternatives": decision_result.alternatives,
                        "metadata": decision_result.metadata
                    },
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"决策制定失败: {e}")
                return jsonify({"success": False, "error": str(e)}), 500
        
        # UI生成API
        @self.app.route('/api/ui/generate', methods=['POST'])
        def generate_ui():
            self.request_count += 1
            try:
                data = request.get_json()
                
                # 构建UI需求
                components = []
                for comp_data in data.get('components', []):
                    component = ComponentConfig(
                        component_type=ComponentType(comp_data['type']),
                        component_id=comp_data['id'],
                        props=comp_data.get('props', {}),
                        styles=comp_data.get('styles', {}),
                        events=comp_data.get('events', {})
                    )
                    components.append(component)
                
                requirements = UIRequirements(
                    layout_type=LayoutType(data.get('layout', 'grid')),
                    theme=ThemeType(data.get('theme', 'light')),
                    components=components,
                    responsive_breakpoints=data.get('breakpoints', {"mobile": 768, "tablet": 1024}),
                    accessibility_features=data.get('accessibility', []),
                    performance_requirements=data.get('performance', {}),
                    user_preferences=data.get('user_preferences', {}),
                    context=data.get('context', {})
                )
                
                # 生成界面
                ui_result = asyncio.run(
                    self.ui_generator.generate_interface(requirements)
                )
                
                return jsonify({
                    "success": True,
                    "ui": ui_result,
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"UI生成失败: {e}")
                return jsonify({"success": False, "error": str(e)}), 500
        
        # API状态管理
        @self.app.route('/api/state/endpoints', methods=['GET'])
        def get_api_endpoints():
            self.request_count += 1
            endpoints = self.api_state_manager.list_endpoints()
            return jsonify({
                "success": True,
                "endpoints": [
                    {
                        "endpoint_id": ep.endpoint_id,
                        "path": ep.path,
                        "method": ep.method,
                        "status": ep.status.value,
                        "response_time": ep.response_time,
                        "error_count": ep.error_count
                    }
                    for ep in endpoints
                ],
                "timestamp": datetime.now().isoformat()
            })
        
        @self.app.route('/api/state/transition', methods=['POST'])
        def trigger_state_transition():
            self.request_count += 1
            try:
                data = request.get_json()
                endpoint_id = data.get('endpoint_id')
                trigger = data.get('trigger')
                context = data.get('context', {})
                
                success = asyncio.run(
                    self.api_state_manager.trigger_transition(endpoint_id, trigger, context)
                )
                
                return jsonify({
                    "success": success,
                    "endpoint_id": endpoint_id,
                    "trigger": trigger,
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"状态转换失败: {e}")
                return jsonify({"success": False, "error": str(e)}), 500
        
        # MCP协作API
        @self.app.route('/api/mcp/discover', methods=['GET'])
        def discover_mcps():
            self.request_count += 1
            try:
                capabilities = request.args.getlist('capabilities')
                mcps = asyncio.run(
                    self.coordinator_client.discover_mcps(capabilities if capabilities else None)
                )
                
                return jsonify({
                    "success": True,
                    "mcps": [
                        {
                            "mcp_id": mcp.mcp_id,
                            "name": mcp.name,
                            "endpoint": mcp.endpoint,
                            "capabilities": mcp.capabilities,
                            "status": mcp.status.value,
                            "response_time": mcp.response_time
                        }
                        for mcp in mcps
                    ],
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"MCP发现失败: {e}")
                return jsonify({"success": False, "error": str(e)}), 500
        
        @self.app.route('/api/mcp/collaborate', methods=['POST'])
        def start_collaboration():
            self.request_count += 1
            try:
                data = request.get_json()
                
                collaboration_type = CollaborationType(data.get('type', 'data_exchange'))
                required_capabilities = data.get('capabilities', [])
                context = data.get('context', {})
                
                session_id = asyncio.run(
                    self.mcp_collaborator.initiate_collaboration(
                        collaboration_type, required_capabilities, context
                    )
                )
                
                return jsonify({
                    "success": True,
                    "session_id": session_id,
                    "collaboration_type": collaboration_type.value,
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"协作启动失败: {e}")
                return jsonify({"success": False, "error": str(e)}), 500
        
        # 工作流API
        @self.app.route('/api/workflow/list', methods=['GET'])
        def list_workflows():
            self.request_count += 1
            workflows = self.workflow_driver.list_available_workflows()
            return jsonify({
                "success": True,
                "workflows": workflows,
                "timestamp": datetime.now().isoformat()
            })
        
        @self.app.route('/api/workflow/start', methods=['POST'])
        def start_workflow():
            self.request_count += 1
            try:
                data = request.get_json()
                
                workflow_id = data.get('workflow_id')
                input_data = data.get('input_data', {})
                ui_preferences = data.get('ui_preferences', {})
                
                execution_id = asyncio.run(
                    self.workflow_driver.start_workflow(workflow_id, input_data, ui_preferences)
                )
                
                return jsonify({
                    "success": True,
                    "execution_id": execution_id,
                    "workflow_id": workflow_id,
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"工作流启动失败: {e}")
                return jsonify({"success": False, "error": str(e)}), 500
        
        @self.app.route('/api/workflow/status/<execution_id>', methods=['GET'])
        def get_workflow_status(execution_id):
            self.request_count += 1
            status = self.workflow_driver.get_workflow_status(execution_id)
            
            if status:
                return jsonify({
                    "success": True,
                    "status": status,
                    "timestamp": datetime.now().isoformat()
                })
            else:
                return jsonify({
                    "success": False,
                    "error": "工作流执行不存在"
                }), 404
        
        # 智能适应API
        @self.app.route('/api/adapt', methods=['POST'])
        def intelligent_adaptation():
            self.request_count += 1
            try:
                data = request.get_json()
                
                # 1. 分析用户输入
                user_id = data.get('user_id', 'anonymous')
                user_input = data.get('user_input', {})
                environment = data.get('environment', {})
                
                # 2. 用户行为分析
                user_analysis = asyncio.run(
                    self.user_analyzer.analyze_user_behavior(user_id, user_input)
                )
                
                # 3. 决策制定
                decision_context = DecisionContext(
                    user_id=user_id,
                    current_state=data.get('current_state', {}),
                    user_input=user_input,
                    environment=environment,
                    constraints=data.get('constraints', {}),
                    goals=data.get('goals', [])
                )
                
                decision = asyncio.run(
                    self.decision_engine.make_decision(decision_context)
                )
                
                # 4. 根据决策结果执行相应操作
                adaptation_result = {}
                
                if decision.action == "generate_ui":
                    # 生成新的UI
                    ui_requirements = self._build_ui_requirements_from_decision(
                        decision, user_analysis, environment
                    )
                    ui_result = asyncio.run(
                        self.ui_generator.generate_interface(ui_requirements)
                    )
                    adaptation_result["ui"] = ui_result
                
                elif decision.action == "start_workflow":
                    # 启动工作流
                    workflow_id = decision.metadata.get("workflow_id")
                    if workflow_id:
                        execution_id = asyncio.run(
                            self.workflow_driver.start_workflow(
                                workflow_id, 
                                decision.metadata.get("input_data", {}),
                                decision.metadata.get("ui_preferences", {})
                            )
                        )
                        adaptation_result["workflow_execution"] = execution_id
                
                elif decision.action == "collaborate_mcps":
                    # 启动MCP协作
                    collaboration_type = CollaborationType(
                        decision.metadata.get("collaboration_type", "data_exchange")
                    )
                    session_id = asyncio.run(
                        self.mcp_collaborator.initiate_collaboration(
                            collaboration_type,
                            decision.metadata.get("required_capabilities", []),
                            decision.metadata.get("context", {})
                        )
                    )
                    adaptation_result["collaboration_session"] = session_id
                
                return jsonify({
                    "success": True,
                    "user_analysis": user_analysis,
                    "decision": {
                        "action": decision.action,
                        "confidence": decision.confidence,
                        "reasoning": decision.reasoning
                    },
                    "adaptation_result": adaptation_result,
                    "timestamp": datetime.now().isoformat()
                })
                
            except Exception as e:
                logger.error(f"智能适应失败: {e}")
                return jsonify({"success": False, "error": str(e)}), 500
        
        # 实时状态API
        @self.app.route('/api/status', methods=['GET'])
        def get_system_status():
            self.request_count += 1
            
            # 收集系统状态信息
            status = {
                "server": {
                    "uptime": int((datetime.now() - self.server_start_time).total_seconds()),
                    "request_count": self.request_count,
                    "active_sessions": len(self.active_sessions)
                },
                "components": {
                    "api_state_manager": {
                        "endpoints_count": len(self.api_state_manager.endpoints),
                        "active_transitions": len(self.api_state_manager.active_transitions)
                    },
                    "user_analyzer": {
                        "profiles_count": len(self.user_analyzer.user_profiles),
                        "patterns_count": len(self.user_analyzer.interaction_patterns)
                    },
                    "ui_generator": {
                        "generated_interfaces": len(self.ui_generator.generated_interfaces),
                        "components_available": len(self.ui_generator.component_library.components)
                    },
                    "mcp_collaborator": {
                        "active_collaborations": len(self.mcp_collaborator.active_collaborations)
                    },
                    "workflow_driver": {
                        "available_workflows": len(self.workflow_driver.workflow_definitions),
                        "active_executions": len(self.workflow_driver.active_executions)
                    }
                },
                "timestamp": datetime.now().isoformat()
            }
            
            return jsonify(status)
    
    def _build_ui_requirements_from_decision(self, decision: 'DecisionResult', 
                                           user_analysis: Dict[str, Any],
                                           environment: Dict[str, Any]) -> UIRequirements:
        """根据决策结果构建UI需求"""
        
        # 默认组件
        components = [
            ComponentConfig(
                component_type=ComponentType.CARD,
                component_id="main_content",
                props={"title": "智能界面", "content": "根据您的需求动态生成"},
                styles={},
                events={}
            )
        ]
        
        # 根据决策元数据添加组件
        if "components" in decision.metadata:
            for comp_data in decision.metadata["components"]:
                component = ComponentConfig(
                    component_type=ComponentType(comp_data["type"]),
                    component_id=comp_data["id"],
                    props=comp_data.get("props", {}),
                    styles=comp_data.get("styles", {}),
                    events=comp_data.get("events", {})
                )
                components.append(component)
        
        # 根据用户偏好选择主题和布局
        theme = ThemeType.LIGHT
        layout = LayoutType.GRID
        
        if user_analysis.get("preferences"):
            prefs = user_analysis["preferences"]
            if prefs.get("theme"):
                theme = ThemeType(prefs["theme"])
            if prefs.get("layout"):
                layout = LayoutType(prefs["layout"])
        
        # 根据环境选择响应式断点
        breakpoints = {"mobile": 768, "tablet": 1024, "desktop": 1200}
        if environment.get("device_type") == "mobile":
            breakpoints = {"mobile": 480, "tablet": 768, "desktop": 1024}
        
        return UIRequirements(
            layout_type=layout,
            theme=theme,
            components=components,
            responsive_breakpoints=breakpoints,
            accessibility_features=decision.metadata.get("accessibility", []),
            performance_requirements=decision.metadata.get("performance", {}),
            user_preferences=user_analysis.get("preferences", {}),
            context=decision.metadata.get("context", {})
        )
    
    def _get_main_page_template(self) -> str:
        """获取主页面模板"""
        return """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SmartUI Enhanced - 智能交互界面系统</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 3rem;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            text-align: center;
            max-width: 800px;
            width: 90%;
        }
        
        .logo {
            font-size: 3rem;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1rem;
        }
        
        .subtitle {
            font-size: 1.2rem;
            color: #666;
            margin-bottom: 2rem;
        }
        
        .features {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1.5rem;
            margin: 2rem 0;
        }
        
        .feature {
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }
        
        .feature h3 {
            color: #333;
            margin-bottom: 0.5rem;
        }
        
        .feature p {
            color: #666;
            font-size: 0.9rem;
        }
        
        .api-info {
            background: #e3f2fd;
            padding: 1.5rem;
            border-radius: 10px;
            margin-top: 2rem;
        }
        
        .api-info h3 {
            color: #1976d2;
            margin-bottom: 1rem;
        }
        
        .endpoint {
            background: #fff;
            padding: 0.5rem 1rem;
            border-radius: 5px;
            margin: 0.5rem 0;
            font-family: 'Courier New', monospace;
            font-size: 0.9rem;
            color: #333;
        }
        
        .status {
            display: inline-block;
            background: #4caf50;
            color: white;
            padding: 0.25rem 0.75rem;
            border-radius: 15px;
            font-size: 0.8rem;
            margin-top: 1rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">SmartUI Enhanced</div>
        <div class="subtitle">智能交互界面生成与管理系统</div>
        
        <div class="features">
            <div class="feature">
                <h3>🎨 动态UI生成</h3>
                <p>根据用户需求和环境变化实时生成优化的用户界面</p>
            </div>
            <div class="feature">
                <h3>🧠 智能决策引擎</h3>
                <p>基于用户行为分析和上下文感知的智能决策系统</p>
            </div>
            <div class="feature">
                <h3>🔗 MCP协作</h3>
                <p>与其他MCP深度集成，实现多系统协同工作</p>
            </div>
            <div class="feature">
                <h3>⚡ 工作流驱动</h3>
                <p>基于工作流的自动化界面生成和状态管理</p>
            </div>
        </div>
        
        <div class="api-info">
            <h3>🚀 API 接口</h3>
            <div class="endpoint">POST /api/adapt - 智能适应接口</div>
            <div class="endpoint">POST /api/ui/generate - UI生成接口</div>
            <div class="endpoint">POST /api/workflow/start - 工作流启动</div>
            <div class="endpoint">POST /api/mcp/collaborate - MCP协作</div>
            <div class="endpoint">GET /api/status - 系统状态</div>
        </div>
        
        <div class="status">🟢 系统运行正常</div>
    </div>
    
    <script>
        // 简单的状态检查
        fetch('/api/status')
            .then(response => response.json())
            .then(data => {
                console.log('系统状态:', data);
            })
            .catch(error => {
                console.error('状态检查失败:', error);
                document.querySelector('.status').textContent = '🔴 系统状态异常';
                document.querySelector('.status').style.background = '#f44336';
            });
    </script>
</body>
</html>
        """
    
    def run(self):
        """启动服务器"""
        logger.info(f"SmartUI Enhanced 服务器启动中...")
        logger.info(f"地址: http://{self.host}:{self.port}")
        logger.info(f"API文档: http://{self.host}:{self.port}/api/status")
        
        self.app.run(
            host=self.host,
            port=self.port,
            debug=False,
            threaded=True
        )

if __name__ == "__main__":
    # 创建并启动服务器
    server = SmartUIEnhancedServer(host="0.0.0.0", port=5002)
    server.run()

