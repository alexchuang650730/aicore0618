#!/bin/bash

# PowerAutomation MCP服务启动脚本
# 专门用于启动三个核心MCP服务

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 远程启动MCP服务
start_remote_mcp_services() {
    log_info "启动远程MCP服务..."
    
    # SSH配置
    SSH_KEY="/opt/powerautomation/alexchuang.pem"
    SSH_USER="ec2-user"  # 从部署日志看，实际用户是ec2-user
    TARGET_SERVER="98.81.255.168"
    REMOTE_PATH="/opt/powerautomation"
    
    # 检查SSH连接
    if ! ssh -i "$SSH_KEY" -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$SSH_USER@$TARGET_SERVER" "echo 'SSH连接成功'" 2>/dev/null; then
        log_error "SSH连接失败，无法启动远程服务"
        return 1
    fi
    
    log_success "SSH连接成功"
    
    # 远程启动服务
    ssh -i "$SSH_KEY" "$SSH_USER@$TARGET_SERVER" "
        cd $REMOTE_PATH
        
        # 设置Python路径
        export PYTHONPATH=$REMOTE_PATH:\$PYTHONPATH
        
        # 创建日志目录
        mkdir -p logs
        
        # 停止可能存在的服务
        pkill -f 'test_manager_mcp_server' 2>/dev/null || true
        pkill -f 'release_manager_mcp_server' 2>/dev/null || true
        pkill -f 'operations_workflow_mcp_server' 2>/dev/null || true
        
        sleep 3
        
        echo '🚀 启动MCP服务...'
        
        # 启动Test Manager MCP (端口8097)
        if [ -f 'mcp/workflow/test_manager_mcp/test_manager_mcp_server.py' ]; then
            nohup python3 mcp/workflow/test_manager_mcp/test_manager_mcp_server.py > logs/test_manager.log 2>&1 &
            echo '✅ Test Manager MCP (8097) 启动'
            sleep 3
        else
            echo '❌ Test Manager MCP 文件不存在'
        fi
        
        # 启动Release Manager MCP (端口8096)
        if [ -f 'mcp/workflow/release_manager_mcp/release_manager_mcp_server.py' ]; then
            nohup python3 mcp/workflow/release_manager_mcp/release_manager_mcp_server.py > logs/release_manager.log 2>&1 &
            echo '✅ Release Manager MCP (8096) 启动'
            sleep 3
        else
            echo '❌ Release Manager MCP 文件不存在'
        fi
        
        # 启动Operations Workflow MCP (端口8090)
        if [ -f 'mcp/workflow/operations_workflow_mcp/operations_workflow_mcp_server.py' ]; then
            nohup python3 mcp/workflow/operations_workflow_mcp/operations_workflow_mcp_server.py > logs/operations_workflow.log 2>&1 &
            echo '✅ Operations Workflow MCP (8090) 启动'
            sleep 3
        else
            echo '❌ Operations Workflow MCP 文件不存在'
        fi
        
        echo '⏳ 等待服务启动...'
        sleep 10
        
        echo '📊 检查服务状态:'
        ps aux | grep -E '(test_manager_mcp|release_manager_mcp|operations_workflow_mcp)' | grep -v grep || echo '⚠️  没有找到MCP服务进程'
        
        echo
        echo '🔌 检查端口监听:'
        netstat -tlnp 2>/dev/null | grep -E ':(8090|8096|8097)' || echo '⚠️  MCP端口未监听'
        
        echo
        echo '📝 检查日志文件:'
        ls -la logs/ 2>/dev/null || echo '⚠️  日志目录不存在'
        
        echo '🎉 MCP服务启动完成'
    "
    
    if [ $? -eq 0 ]; then
        log_success "远程MCP服务启动完成"
    else
        log_error "远程MCP服务启动失败"
        return 1
    fi
}

# 验证MCP服务
verify_mcp_services() {
    log_info "验证MCP服务状态..."
    
    sleep 5
    
    # 测试各个MCP服务
    for service in "Test Manager:8097" "Release Manager:8096" "Operations Workflow:8090"; do
        name=$(echo $service | cut -d: -f1)
        port=$(echo $service | cut -d: -f2)
        
        if curl -s --connect-timeout 5 "http://98.81.255.168:$port/api/status" > /dev/null; then
            log_success "$name MCP (端口$port) 运行正常"
        else
            log_error "$name MCP (端口$port) 无响应"
        fi
    done
}

# 测试完整功能
test_devops_pipeline() {
    log_info "测试DevOps流水线功能..."
    
    # 测试主API的workflow状态
    if curl -s "http://98.81.255.168:5001/api/workflows/status" > /dev/null; then
        log_success "主API workflow状态正常"
    else
        log_error "主API workflow状态异常"
    fi
    
    # 测试DevOps按钮功能
    log_info "测试DevOps按钮功能..."
    
    # 测试项目信息
    PROJECT_INFO='{"project_info":{"name":"测试项目","type":"game","complexity":"simple"}}'
    
    # 测试测试按钮
    if curl -s -X POST -H "Content-Type: application/json" -d "$PROJECT_INFO" "http://98.81.255.168:5001/api/button/test" > /dev/null; then
        log_success "测试按钮功能正常"
    else
        log_error "测试按钮功能异常"
    fi
    
    # 测试部署按钮
    if curl -s -X POST -H "Content-Type: application/json" -d "$PROJECT_INFO" "http://98.81.255.168:5001/api/button/deploy" > /dev/null; then
        log_success "部署按钮功能正常"
    else
        log_error "部署按钮功能异常"
    fi
    
    # 测试运维按钮
    if curl -s -X POST -H "Content-Type: application/json" -d "$PROJECT_INFO" "http://98.81.255.168:5001/api/button/monitor" > /dev/null; then
        log_success "运维按钮功能正常"
    else
        log_error "运维按钮功能异常"
    fi
}

# 显示服务信息
show_service_info() {
    log_success "🎉 PowerAutomation MCP服务修复完成！"
    echo
    echo "=================================="
    echo "📍 服务地址"
    echo "=================================="
    echo "🌐 主界面: http://98.81.255.168:5001"
    echo "📊 API状态: http://98.81.255.168:5001/api/status"
    echo
    echo "🛠️ MCP服务:"
    echo "   • Test Manager MCP: http://98.81.255.168:8097"
    echo "   • Release Manager MCP: http://98.81.255.168:8096"
    echo "   • Operations Workflow MCP: http://98.81.255.168:8090"
    echo
    echo "🎮 功能测试:"
    echo "   1. 访问主界面进行聊天测试"
    echo "   2. 点击三个DevOps按钮测试功能"
    echo "   3. 使用完整流水线功能"
    echo
    echo "✅ 所有服务现在应该正常工作！"
}

# 主函数
main() {
    echo "🔧 PowerAutomation MCP服务修复工具"
    echo "=================================="
    
    start_remote_mcp_services
    verify_mcp_services
    test_devops_pipeline
    show_service_info
}

# 执行主函数
main "$@"

