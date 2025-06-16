#!/usr/bin/env python3
"""
需求分析MCP服务器
Requirements Analysis MCP Server

基于Flask的HTTP API服务器，提供需求分析智能引擎功能
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
sys.path.append(str(project_root / "mcp" / "workflow" / "requirements_analysis_mcp" / "src"))
sys.path.append(str(project_root / "workflow_howto"))

try:
    from requirements_analysis_mcp import RequirementAnalysisMCP
    print("✅ 成功导入需求分析MCP")
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    print(f"当前路径: {os.getcwd()}")
    print(f"Python路径: {sys.path}")
    sys.exit(1)

# 创建Flask应用
app = Flask(__name__)
CORS(app)  # 允许跨域访问

# 初始化需求分析MCP
requirements_mcp = RequirementAnalysisMCP()

@app.route('/', methods=['GET'])
def home():
    """首页"""
    return jsonify({
        "service": "Requirements Analysis MCP",
        "version": "1.0.0",
        "status": "running",
        "port": 8094,
        "endpoints": {
            "health": "/health",
            "analyze": "/analyze", 
            "capabilities": "/capabilities",
            "test": "/test"
        },
        "timestamp": datetime.now().isoformat()
    })

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        "service": "Requirements Analysis MCP",
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
                "requirements_parsing": True,
                "feasibility_analysis": True,
                "solution_generation": True,
                "roadmap_planning": True,
                "complexity_assessment": True,
                "domain_analysis": True
            },
            "supported_domains": [
                "OCR", "NLP", "Web", "AI", "Vision", "Other"
            ],
            "service_info": {
                "name": "Requirements Analysis MCP",
                "version": "1.0.0",
                "port": 8094
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/analyze', methods=['POST'])
def analyze_requirements():
    """需求分析接口"""
    try:
        request_data = request.get_json()
        
        if not request_data:
            return jsonify({
                "success": False,
                "error": "请提供JSON格式的请求数据"
            }), 400
        
        # 运行异步分析
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            result = loop.run_until_complete(
                requirements_mcp.analyze_requirements(request_data)
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
                "business_requirements": "开发繁体中文OCR系统，提升识别准确度",
                "technical_constraints": ["云端部署", "高可用性"],
                "domain": "OCR"
            }
            
            result = loop.run_until_complete(
                requirements_mcp.analyze_requirements(test_request)
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
    print("🚀 启动需求分析MCP服务器...")
    print("📍 服务地址: http://98.81.255.168:8094")
    print("📋 服务功能: 智能需求分析")
    
    app.run(
        host='0.0.0.0',
        port=8094,
        debug=False,
        threaded=True
    )

