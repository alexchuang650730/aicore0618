#!/bin/bash

# SmartUI DevOps系统启动脚本
# 用于快速启动完整的DevOps集成系统

echo "🚀 启动 SmartUI DevOps 集成系统..."
echo "=================================="

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到Python3"
    exit 1
fi

# 检查工作目录
if [ ! -d "/opt/powerautomation" ]; then
    echo "❌ 错误: PowerAutomation目录不存在"
    exit 1
fi

# 切换到工作目录
cd /opt/powerautomation

# 检查必要文件
required_files=(
    "smartui_devops_api_server.py"
    "smartui_devops_dashboard.html"
    "mcp/workflow/test_manager_mcp/test_manager_mcp.py"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ 错误: 缺少必要文件 $file"
        exit 1
    fi
done

echo "✅ 环境检查通过"

# 设置Python路径
export PYTHONPATH="/opt/powerautomation:$PYTHONPATH"

# 检查端口占用
if netstat -tlnp 2>/dev/null | grep -q ":5001 "; then
    echo "⚠️  警告: 端口5001已被占用，尝试终止占用进程..."
    
    # 获取占用进程PID
    PID=$(netstat -tlnp 2>/dev/null | grep ":5001 " | awk '{print $7}' | cut -d'/' -f1)
    
    if [ ! -z "$PID" ]; then
        echo "🔄 终止进程 $PID..."
        kill $PID 2>/dev/null
        sleep 2
    fi
fi

# 启动API服务器
echo "🔧 启动 SmartUI DevOps API 服务器..."
python3 smartui_devops_api_server.py &
SERVER_PID=$!

# 等待服务器启动
echo "⏳ 等待服务器启动..."
sleep 3

# 检查服务器状态
if kill -0 $SERVER_PID 2>/dev/null; then
    echo "✅ API服务器启动成功 (PID: $SERVER_PID)"
    
    # 测试API状态
    if curl -s http://localhost:5001/api/status > /dev/null; then
        echo "✅ API服务器响应正常"
        
        echo ""
        echo "🎉 SmartUI DevOps 系统启动完成！"
        echo "=================================="
        echo "📍 访问地址: http://localhost:5001"
        echo "📊 API状态: http://localhost:5001/api/status"
        echo "🔧 Workflow状态: http://localhost:5001/api/workflows/status"
        echo ""
        echo "🛠️  可用功能:"
        echo "   • 智能代码生成"
        echo "   • 自动化测试 (Test Manager MCP)"
        echo "   • 一键部署 (Release Manager MCP)"
        echo "   • 运维监控 (Operations Workflow MCP)"
        echo "   • 完整DevOps流水线"
        echo ""
        echo "📝 使用方法:"
        echo "   1. 在浏览器中打开 http://localhost:5001"
        echo "   2. 在聊天框中描述您的项目需求"
        echo "   3. 使用DevOps按钮进行测试、部署和监控"
        echo ""
        echo "🔄 停止服务: kill $SERVER_PID"
        echo "📖 文档: /opt/powerautomation/SmartUI_DevOps_部署文档.md"
        
    else
        echo "❌ API服务器无响应"
        kill $SERVER_PID 2>/dev/null
        exit 1
    fi
else
    echo "❌ API服务器启动失败"
    exit 1
fi

# 保持脚本运行，等待用户中断
echo ""
echo "按 Ctrl+C 停止服务..."
trap "echo '🛑 正在停止服务...'; kill $SERVER_PID 2>/dev/null; echo '✅ 服务已停止'; exit 0" INT

# 等待服务器进程
wait $SERVER_PID

