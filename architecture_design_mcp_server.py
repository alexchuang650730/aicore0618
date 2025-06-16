#!/usr/bin/env python3
"""
架构设计MCP服务器
Architecture Design MCP Server

基于Flask的HTTP API服务器，提供架构设计智能引擎功能
"""

import sys
import os
import asyncio
from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / "mcp" / "workflow" / "architecture_design_mcp" / "src"))
sys.path.append(str(project_root / "workflow_howto"))

try:
    from architecture_design_mcp import ArchitectureDesignMCP
    print("✅ 成功导入架构设计MCP")
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    print(f"当前路径: {os.getcwd()}")
    print(f"Python路径: {sys.path}")
    sys.exit(1)

# 创建Flask应用
app = Flask(__name__)
CORS(app)  # 允许跨域访问

# 初始化架构设计MCP
architecture_mcp = ArchitectureDesignMCP()

@app.route('/', methods=['GET'])
def home():
    """首页"""
    return jsonify({
        "service": "Architecture Design MCP",
        "version": "1.0.0",
        "status": "running",
        "port": 8095,
        "endpoints": {
            "health": "/health",
            "design": "/design", 
            "capabilities": "/capabilities",
            "test": "/test"
        },
        "timestamp": datetime.now().isoformat()
    })

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        "service": "Architecture Design MCP",
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/capabilities', methods=['GET'])
def get_capabilities():
    """获取能力信息"""
    try:
        return jsonify({
            "success": True,
            "capabilities": {
                "architecture_design": True,
                "pattern_recommendation": True,
                "technology_selection": True,
                "scalability_analysis": True,
                "security_design": True,
                "performance_optimization": True
            },
            "supported_patterns": [
                "Microservices", "Monolithic", "Serverless", 
                "Layered", "Event-Driven", "Hexagonal"
            ],
            "service_info": {
                "name": "Architecture Design MCP",
                "version": "1.0.0",
                "port": 8095
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/design', methods=['POST'])
def design_architecture():
    """架构设计接口"""
    try:
        request_data = request.get_json()
        
        if not request_data:
            return jsonify({
                "success": False,
                "error": "请提供JSON格式的请求数据"
            }), 400
        
        # 运行异步设计
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                architecture_mcp.design_architecture(request_data)
            )
            
            return jsonify({
                "success": True,
                "result": result,
                "timestamp": datetime.now().isoformat()
            })
            
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/test', methods=['GET'])
def test_service():
    """测试服务"""
    try:
        # 运行测试用例
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            test_request = {
                "requirements_analysis_result": {
                    "parsed_requirements": [
                        {"id": "req_1", "text": "高性能OCR识别", "complexity": 0.8}
                    ],
                    "domain": "OCR",
                    "scale": "medium"
                },
                "system_constraints": {
                    "budget": "medium",
                    "timeline": "6个月",
                    "team_size": 5
                }
            }
            
            result = loop.run_until_complete(
                architecture_mcp.design_architecture(test_request)
            )
            
            return jsonify({
                "success": True,
                "test_result": result,
                "message": "测试通过",
                "timestamp": datetime.now().isoformat()
            })
            
        finally:
            loop.close()
            
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "message": "测试失败"
        }), 500

if __name__ == '__main__':
    print("🚀 启动架构设计MCP服务器...")
    print("📍 服务地址: http://98.81.255.168:8095")
    print("🏗️ 服务功能: 智能架构设计")
    
    app.run(
        host='0.0.0.0',
        port=8095,
        debug=False,
        threaded=True
    )

