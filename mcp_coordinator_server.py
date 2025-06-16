#!/usr/bin/env python3
"""
MCP协调器服务器
在端口8089提供MCP协调器界面
"""

from flask import Flask, jsonify, render_template_string
from flask_cors import CORS
import json
from datetime import datetime

app = Flask(__name__)
CORS(app)

# MCP服务注册表
MCP_SERVICES = [
    {
        "name": "KILOCODE MCP",
        "status": "✅ 运行中",
        "port": 8080,
        "description": "兜底创建引擎"
    },
    {
        "name": "RELEASE MANAGER_MCP", 
        "status": "✅ 运行中",
        "port": 8091,
        "description": "发布管理引擎"
    },
    {
        "name": "SMART UI_MCP",
        "status": "✅ 运行中", 
        "port": 8092,
        "description": "智能界面引擎"
    },
    {
        "name": "TEST MANAGER_MCP",
        "status": "✅ 运行中",
        "port": 8093,
        "description": "测试管理引擎"
    },
    {
        "name": "REQUIREMENTS ANALYSIS_MCP",
        "status": "✅ 运行中",
        "port": 8094,
        "description": "需求分析智能引擎"
    },
    {
        "name": "ARCHITECTURE DESIGN_MCP",
        "status": "✅ 运行中", 
        "port": 8095,
        "description": "架构设计智能引擎"
    }
]

# MCP协调器界面HTML
COORDINATOR_HTML = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MCP协调器</title>
    <style>
        body {
            font-family: 'Microsoft YaHei', Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        .title {
            font-size: 28px;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        }
        .status {
            font-size: 16px;
            color: #28a745;
            margin-bottom: 5px;
        }
        .subtitle {
            font-size: 14px;
            color: #666;
        }
        .mcp-list {
            margin-top: 20px;
        }
        .mcp-item {
            display: flex;
            align-items: center;
            padding: 15px 0;
            border-bottom: 1px solid #eee;
        }
        .mcp-item:last-child {
            border-bottom: none;
        }
        .mcp-bullet {
            margin-right: 10px;
            font-size: 16px;
        }
        .mcp-name {
            font-weight: bold;
            color: #333;
        }
        .mcp-status {
            margin-left: 10px;
            color: #28a745;
        }
        .refresh-btn {
            background: #007bff;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin-top: 20px;
        }
        .refresh-btn:hover {
            background: #0056b3;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="title">MCP协调器</div>
            <div class="status">运行中</div>
            <div class="subtitle">统一工作流协调 | 智能介入管理</div>
        </div>
        
        <div class="mcp-list" id="mcpList">
            <!-- MCP服务列表将通过JavaScript动态加载 -->
        </div>
        
        <button class="refresh-btn" onclick="loadMCPServices()">刷新状态</button>
    </div>

    <script>
        function loadMCPServices() {
            fetch('/coordinator/mcps/api')
                .then(response => response.json())
                .then(data => {
                    const mcpList = document.getElementById('mcpList');
                    mcpList.innerHTML = '';
                    
                    data.services.forEach(service => {
                        const item = document.createElement('div');
                        item.className = 'mcp-item';
                        item.innerHTML = `
                            <span class="mcp-bullet">•</span>
                            <span class="mcp-name">${service.name}:</span>
                            <span class="mcp-status">${service.status}</span>
                        `;
                        mcpList.appendChild(item);
                    });
                })
                .catch(error => {
                    console.error('加载MCP服务失败:', error);
                });
        }
        
        // 页面加载时自动加载MCP服务
        document.addEventListener('DOMContentLoaded', loadMCPServices);
        
        // 每30秒自动刷新
        setInterval(loadMCPServices, 30000);
    </script>
</body>
</html>
"""

@app.route('/coordinator/mcps')
def coordinator_mcps():
    """MCP协调器主界面"""
    return COORDINATOR_HTML

@app.route('/coordinator/mcps/api')
def coordinator_mcps_api():
    """MCP服务API接口"""
    return jsonify({
        "success": True,
        "timestamp": datetime.now().isoformat(),
        "services": MCP_SERVICES,
        "total_count": len(MCP_SERVICES)
    })

@app.route('/coordinator/mcps/register', methods=['POST'])
def register_mcp():
    """注册新的MCP服务"""
    try:
        from flask import request
        service_data = request.get_json()
        
        # 检查是否已存在
        existing = next((s for s in MCP_SERVICES if s['name'] == service_data['name']), None)
        if existing:
            existing.update(service_data)
            return jsonify({"success": True, "message": "MCP服务已更新"})
        else:
            MCP_SERVICES.append(service_data)
            return jsonify({"success": True, "message": "MCP服务已注册"})
            
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/health')
def health():
    """健康检查"""
    return jsonify({
        "service": "MCP Coordinator",
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "mcp_count": len(MCP_SERVICES)
    })

if __name__ == '__main__':
    print("🚀 启动MCP协调器服务器...")
    print("📍 服务地址: http://98.81.255.168:8089")
    print("🌐 协调器界面: http://98.81.255.168:8089/coordinator/mcps")
    print("📊 API接口: http://98.81.255.168:8089/coordinator/mcps/api")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=8089, debug=False)

