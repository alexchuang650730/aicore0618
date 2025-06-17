#!/usr/bin/env python3
"""
SmartUI DevOps API Server - 远程部署版本
为SmartUI提供完整的DevOps功能，集成三个workflow MCP
运行在98.81.255.168:5001
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import requests
import json
import logging
import time
from datetime import datetime
import asyncio
import threading

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)
CORS(app)

# Workflow端点配置 - 远程部署版本
WORKFLOW_ENDPOINTS = {
    "test_manager": "http://98.81.255.168:8097",
    "release_manager": "http://98.81.255.168:8096", 
    "operations_workflow": "http://98.81.255.168:8090"
}

class DevOpsWorkflowClient:
    """DevOps工作流客户端 - 集成三个workflow"""
    
    def __init__(self):
        self.endpoints = WORKFLOW_ENDPOINTS
        logger.info("✅ DevOps Workflow Client 初始化完成")
        logger.info(f"🔗 Test Manager: {self.endpoints['test_manager']}")
        logger.info(f"🔗 Release Manager: {self.endpoints['release_manager']}")
        logger.info(f"🔗 Operations Workflow: {self.endpoints['operations_workflow']}")
    
    def call_workflow(self, workflow_name, action, params):
        """调用指定的workflow MCP"""
        try:
            endpoint = self.endpoints.get(workflow_name)
            if not endpoint:
                return {"success": False, "error": f"未知的workflow: {workflow_name}"}
            
            url = f"{endpoint}/mcp/request"
            payload = {
                "action": action,
                "params": params
            }
            
            logger.info(f"📨 调用 {workflow_name}: {action}")
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "success": False, 
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"调用 {workflow_name} 失败: {e}")
            return {"success": False, "error": str(e)}
    
    def test_workflow(self, project_info):
        """调用Test Manager MCP进行测试"""
        return self.call_workflow("test_manager", "full_test_cycle", {
            "project_info": project_info
        })
    
    def deploy_workflow(self, project_info, test_result=None):
        """调用Release Manager MCP进行部署"""
        return self.call_workflow("release_manager", "deployment_verification", {
            "project_info": project_info,
            "test_results": test_result
        })
    
    def monitor_workflow(self, project_info, pipeline_result=None):
        """调用Operations Workflow MCP进行监控设置"""
        return self.call_workflow("operations_workflow", "setup_monitoring", {
            "project_info": project_info,
            "pipeline_result": pipeline_result
        })

# 初始化DevOps客户端
devops_client = DevOpsWorkflowClient()

# 基础路由
@app.route('/')
def index():
    return send_from_directory('/opt/powerautomation', 'smartui_devops_dashboard.html')

@app.route('/api/status')
def api_status():
    """API状态检查"""
    return jsonify({
        "success": True,
        "service": "SmartUI DevOps API Server",
        "version": "3.0.0",
        "status": "running",
        "deployment": "remote",
        "server": "98.81.255.168:5001",
        "workflows": {
            "test_manager": WORKFLOW_ENDPOINTS["test_manager"],
            "release_manager": WORKFLOW_ENDPOINTS["release_manager"],
            "operations_workflow": WORKFLOW_ENDPOINTS["operations_workflow"]
        },
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/workflows/status')
def workflows_status():
    """检查所有workflow的状态"""
    status_results = {}
    
    for name, endpoint in WORKFLOW_ENDPOINTS.items():
        try:
            response = requests.get(f"{endpoint}/api/status", timeout=5)
            if response.status_code == 200:
                status_results[name] = {
                    "status": "healthy",
                    "endpoint": endpoint,
                    "response": response.json()
                }
            else:
                status_results[name] = {
                    "status": "unhealthy",
                    "endpoint": endpoint,
                    "error": f"HTTP {response.status_code}"
                }
        except Exception as e:
            status_results[name] = {
                "status": "unreachable",
                "endpoint": endpoint,
                "error": str(e)
            }
    
    return jsonify({
        "success": True,
        "workflows": status_results,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/chat', methods=['POST'])
def api_chat():
    """聊天接口 - 生成项目代码"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        logger.info(f"💬 收到聊天请求: {message}")
        
        # 模拟AI处理过程
        processing_steps = [
            {"step": "🔍 需求分析中...", "progress": 20, "duration": 2},
            {"step": "🧠 智能路由决策中...", "progress": 40, "duration": 2},
            {"step": "⚙️ 选择最佳工作流...", "progress": 60, "duration": 2},
            {"step": "💻 生成解决方案...", "progress": 80, "duration": 2},
            {"step": "✅ 处理完成", "progress": 100, "duration": 1}
        ]
        
        # 智能项目识别
        project_type = "game" if "游戏" in message or "贪吃蛇" in message else "web_app"
        project_name = "贪吃蛇游戏" if "贪吃蛇" in message else "智能应用"
        
        # 生成项目代码（示例）
        if "贪吃蛇" in message:
            code_content = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>贪吃蛇游戏 - PowerAutomation生成</title>
    <style>
        body { margin: 0; padding: 20px; background: #1a1a1a; color: white; font-family: Arial, sans-serif; }
        .game-container { text-align: center; }
        canvas { border: 2px solid #00ff00; background: #000; }
        .controls { margin: 20px 0; }
        .score { font-size: 24px; margin: 10px 0; }
        .architecture-info { 
            background: #2a2a2a; padding: 15px; margin: 20px 0; 
            border-radius: 8px; text-align: left; 
        }
    </style>
</head>
<body>
    <div class="game-container">
        <h1>🐍 贪吃蛇游戏</h1>
        <div class="score">得分: <span id="score">0</span></div>
        <canvas id="gameCanvas" width="400" height="400"></canvas>
        <div class="controls">
            <p>使用方向键控制蛇的移动</p>
            <button onclick="startGame()">开始游戏</button>
            <button onclick="pauseGame()">暂停</button>
        </div>
        
        <div class="architecture-info">
            <h3>🏗️ 架构设计信息</h3>
            <p><strong>架构模式:</strong> 单体应用 + 组件化设计</p>
            <p><strong>技术栈:</strong> HTML5 Canvas + JavaScript ES6</p>
            <p><strong>核心组件:</strong></p>
            <ul>
                <li>GameEngine - 游戏引擎核心</li>
                <li>Snake - 蛇对象管理</li>
                <li>Food - 食物生成系统</li>
                <li>Renderer - 渲染引擎</li>
                <li>InputHandler - 输入处理</li>
            </ul>
            <p><strong>性能优化:</strong> Canvas渲染优化、事件防抖、内存管理</p>
        </div>
    </div>

    <script>
        class SnakeGame {
            constructor() {
                this.canvas = document.getElementById('gameCanvas');
                this.ctx = this.canvas.getContext('2d');
                this.gridSize = 20;
                this.tileCount = this.canvas.width / this.gridSize;
                
                this.snake = [
                    {x: 10, y: 10}
                ];
                this.food = {x: 15, y: 15};
                this.dx = 0;
                this.dy = 0;
                this.score = 0;
                this.gameRunning = false;
                
                this.setupEventListeners();
            }
            
            setupEventListeners() {
                document.addEventListener('keydown', (e) => {
                    if (!this.gameRunning) return;
                    
                    switch(e.key) {
                        case 'ArrowUp':
                            if (this.dy !== 1) { this.dx = 0; this.dy = -1; }
                            break;
                        case 'ArrowDown':
                            if (this.dy !== -1) { this.dx = 0; this.dy = 1; }
                            break;
                        case 'ArrowLeft':
                            if (this.dx !== 1) { this.dx = -1; this.dy = 0; }
                            break;
                        case 'ArrowRight':
                            if (this.dx !== -1) { this.dx = 1; this.dy = 0; }
                            break;
                    }
                });
            }
            
            draw() {
                // 清空画布
                this.ctx.fillStyle = 'black';
                this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
                
                // 绘制蛇
                this.ctx.fillStyle = '#00ff00';
                this.snake.forEach(segment => {
                    this.ctx.fillRect(segment.x * this.gridSize, segment.y * this.gridSize, 
                                    this.gridSize - 2, this.gridSize - 2);
                });
                
                // 绘制食物
                this.ctx.fillStyle = '#ff0000';
                this.ctx.fillRect(this.food.x * this.gridSize, this.food.y * this.gridSize, 
                                this.gridSize - 2, this.gridSize - 2);
            }
            
            update() {
                if (!this.gameRunning) return;
                
                const head = {x: this.snake[0].x + this.dx, y: this.snake[0].y + this.dy};
                
                // 检查碰撞
                if (head.x < 0 || head.x >= this.tileCount || 
                    head.y < 0 || head.y >= this.tileCount ||
                    this.snake.some(segment => segment.x === head.x && segment.y === head.y)) {
                    this.gameOver();
                    return;
                }
                
                this.snake.unshift(head);
                
                // 检查是否吃到食物
                if (head.x === this.food.x && head.y === this.food.y) {
                    this.score += 10;
                    document.getElementById('score').textContent = this.score;
                    this.generateFood();
                } else {
                    this.snake.pop();
                }
            }
            
            generateFood() {
                this.food = {
                    x: Math.floor(Math.random() * this.tileCount),
                    y: Math.floor(Math.random() * this.tileCount)
                };
                
                // 确保食物不在蛇身上
                if (this.snake.some(segment => segment.x === this.food.x && segment.y === this.food.y)) {
                    this.generateFood();
                }
            }
            
            start() {
                this.gameRunning = true;
                this.gameLoop();
            }
            
            pause() {
                this.gameRunning = false;
            }
            
            gameOver() {
                this.gameRunning = false;
                alert(`游戏结束！最终得分: ${this.score}`);
            }
            
            gameLoop() {
                this.update();
                this.draw();
                
                if (this.gameRunning) {
                    setTimeout(() => this.gameLoop(), 150);
                }
            }
        }
        
        const game = new SnakeGame();
        
        function startGame() {
            game.start();
        }
        
        function pauseGame() {
            game.pause();
        }
        
        // 自动开始游戏
        game.draw();
    </script>
</body>
</html>"""
        else:
            code_content = f"""# {project_name}
# PowerAutomation AI 生成的智能应用

class SmartApplication:
    def __init__(self):
        self.name = "{project_name}"
        self.version = "1.0.0"
        
    def run(self):
        print(f"启动 {self.name}...")
        return "应用运行成功！"

if __name__ == "__main__":
    app = SmartApplication()
    app.run()
"""
        
        return jsonify({
            "success": True,
            "message": f"✅ 已为您生成 {project_name} 的完整代码！",
            "processing_steps": processing_steps,
            "project_info": {
                "name": project_name,
                "type": project_type,
                "complexity": "simple",
                "description": f"基于AI智能生成的{project_name}"
            },
            "generated_code": code_content,
            "architecture_info": {
                "pattern": "组件化单体应用",
                "tech_stack": ["HTML5", "JavaScript ES6", "Canvas API"],
                "components": ["GameEngine", "Snake", "Food", "Renderer", "InputHandler"],
                "optimizations": ["Canvas渲染优化", "事件防抖", "内存管理"]
            },
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"聊天处理失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/button/test', methods=['POST'])
def api_button_test():
    """测试按钮 - 调用Test Manager MCP"""
    try:
        data = request.get_json()
        project_info = data.get('project_info', {})
        
        logger.info(f"🧪 执行测试: {project_info.get('name', 'Unknown Project')}")
        
        result = devops_client.test_workflow(project_info)
        
        return jsonify({
            "success": True,
            "action": "test",
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"测试执行失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "action": "test"
        }), 500

@app.route('/api/button/deploy', methods=['POST'])
def api_button_deploy():
    """部署按钮 - 调用Release Manager MCP"""
    try:
        data = request.get_json()
        project_info = data.get('project_info', {})
        test_result = data.get('test_result', {})
        
        logger.info(f"🚀 执行部署: {project_info.get('name', 'Unknown Project')}")
        
        result = devops_client.deploy_workflow(project_info, test_result)
        
        return jsonify({
            "success": True,
            "action": "deploy",
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"部署执行失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "action": "deploy"
        }), 500

@app.route('/api/button/monitor', methods=['POST'])
def api_button_monitor():
    """运维按钮 - 调用Operations Workflow MCP"""
    try:
        data = request.get_json()
        project_info = data.get('project_info', {})
        pipeline_result = data.get('pipeline_result', {})
        
        logger.info(f"📊 设置监控: {project_info.get('name', 'Unknown Project')}")
        
        result = devops_client.monitor_workflow(project_info, pipeline_result)
        
        return jsonify({
            "success": True,
            "action": "monitor",
            "result": result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"监控设置失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "action": "monitor"
        }), 500

@app.route('/api/devops/full-pipeline', methods=['POST'])
def api_full_pipeline():
    """完整DevOps流水线"""
    try:
        data = request.get_json()
        project_info = data.get('project_info', {})
        
        project_name = project_info.get('name', 'Unknown Project')
        logger.info(f"🔄 执行完整DevOps流水线: {project_name}")
        
        pipeline_id = f"pipeline_{int(time.time())}"
        start_time = datetime.now()
        
        phases = []
        
        # 阶段1: 测试验证
        logger.info("🧪 执行阶段1: 测试验证")
        test_start = time.time()
        test_result = devops_client.test_workflow(project_info)
        test_duration = time.time() - test_start
        
        phases.append({
            "phase": 1,
            "name": "测试验证",
            "workflow": "test_manager_mcp",
            "status": "completed",
            "duration": round(test_duration, 1),
            "result": test_result.get("results", test_result)
        })
        
        # 阶段2: 部署发布
        logger.info("🚀 执行阶段2: 部署发布")
        deploy_start = time.time()
        deploy_result = devops_client.deploy_workflow(project_info, test_result)
        deploy_duration = time.time() - deploy_start
        
        phases.append({
            "phase": 2,
            "name": "部署发布",
            "workflow": "release_manager_mcp",
            "status": "completed",
            "duration": round(deploy_duration, 1),
            "result": deploy_result.get("results", deploy_result)
        })
        
        # 阶段3: 运维监控
        logger.info("📊 执行阶段3: 运维监控")
        monitor_start = time.time()
        monitor_result = devops_client.monitor_workflow(project_info, {
            "test_result": test_result,
            "deploy_result": deploy_result
        })
        monitor_duration = time.time() - monitor_start
        
        phases.append({
            "phase": 3,
            "name": "运维监控",
            "workflow": "operations_workflow_mcp",
            "status": "completed",
            "duration": round(monitor_duration, 1),
            "result": monitor_result.get("results", monitor_result)
        })
        
        end_time = datetime.now()
        total_duration = round(test_duration + deploy_duration + monitor_duration, 1)
        
        # 判断整体状态
        overall_status = "success"
        if not all(phase.get("result", {}).get("success", True) for phase in phases):
            overall_status = "partial_success"
        
        pipeline_result = {
            "pipeline_id": pipeline_id,
            "project_name": project_name,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "total_duration": total_duration,
            "overall_status": overall_status,
            "phases": phases
        }
        
        return jsonify({
            "success": True,
            "message": f"🎉 DevOps流水线执行完成！状态: {overall_status}",
            "pipeline_result": pipeline_result,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"DevOps流水线执行失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e),
            "action": "full_pipeline"
        }), 500

if __name__ == '__main__':
    logger.info("🚀 启动 SmartUI DevOps API Server (远程部署版本)...")
    logger.info("📍 服务地址: http://98.81.255.168:5001")
    logger.info("🔗 集成三个Workflow MCP:")
    for name, endpoint in WORKFLOW_ENDPOINTS.items():
        logger.info(f"   • {name}: {endpoint}")
    
    app.run(host='0.0.0.0', port=5001, debug=False)

