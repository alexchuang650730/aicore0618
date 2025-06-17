#!/bin/bash

# PowerAutomation 远程服务管理脚本
# 用于管理98.81.255.168上的PowerAutomation服务

# 加载配置
source /opt/powerautomation/deploy_config.sh

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

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查服务状态
check_status() {
    log_info "检查远程服务状态..."
    
    ssh -i "$SSH_KEY" "$SSH_USER@$TARGET_SERVER" "
        echo '=== PowerAutomation 服务状态 ==='
        echo
        echo '📊 进程状态:'
        ps aux | grep -E '(smartui_devops|test_manager|release_manager|operations_workflow)' | grep -v grep || echo '⚠️  没有找到运行中的服务'
        
        echo
        echo '🔌 端口状态:'
        netstat -tlnp 2>/dev/null | grep -E ':(5001|8090|8096|8097)' || echo '⚠️  没有找到监听的端口'
        
        echo
        echo '📁 磁盘使用:'
        df -h $REMOTE_DEPLOY_PATH 2>/dev/null || echo '⚠️  部署目录不存在'
        
        echo
        echo '📝 最新日志 (最后10行):'
        if [ -d '$REMOTE_DEPLOY_PATH/logs' ]; then
            for log in $REMOTE_DEPLOY_PATH/logs/*.log; do
                if [ -f \"\$log\" ]; then
                    echo \"--- \$(basename \$log) ---\"
                    tail -5 \"\$log\" 2>/dev/null || echo '无法读取日志'
                    echo
                fi
            done
        else
            echo '⚠️  日志目录不存在'
        fi
    "
}

# 启动服务
start_services() {
    log_info "启动远程服务..."
    
    ssh -i "$SSH_KEY" "$SSH_USER@$TARGET_SERVER" "
        cd $REMOTE_DEPLOY_PATH
        
        # 检查部署目录
        if [ ! -d '$REMOTE_DEPLOY_PATH' ]; then
            echo 'ERROR: 部署目录不存在，请先运行部署脚本'
            exit 1
        fi
        
        # 创建日志目录
        mkdir -p logs
        
        # 设置Python路径
        export PYTHONPATH=$REMOTE_DEPLOY_PATH:\$PYTHONPATH
        
        echo '🚀 启动服务...'
        
        # 启动Test Manager MCP
        if [ -f 'mcp/workflow/test_manager_mcp/test_manager_mcp_server.py' ]; then
            nohup python3 mcp/workflow/test_manager_mcp/test_manager_mcp_server.py > logs/test_manager.log 2>&1 &
            echo '✅ Test Manager MCP 启动'
            sleep 2
        fi
        
        # 启动Release Manager MCP
        if [ -f 'mcp/workflow/release_manager_mcp/release_manager_mcp_server.py' ]; then
            nohup python3 mcp/workflow/release_manager_mcp/release_manager_mcp_server.py > logs/release_manager.log 2>&1 &
            echo '✅ Release Manager MCP 启动'
            sleep 2
        fi
        
        # 启动Operations Workflow MCP
        if [ -f 'mcp/workflow/operations_workflow_mcp/operations_workflow_mcp_server.py' ]; then
            nohup python3 mcp/workflow/operations_workflow_mcp/operations_workflow_mcp_server.py > logs/operations_workflow.log 2>&1 &
            echo '✅ Operations Workflow MCP 启动'
            sleep 2
        fi
        
        # 启动主API服务器
        if [ -f 'smartui_devops_api_server.py' ]; then
            nohup python3 smartui_devops_api_server.py > logs/smartui_api.log 2>&1 &
            echo '✅ SmartUI API Server 启动'
            sleep 3
        fi
        
        echo '🎉 所有服务启动完成'
    "
    
    log_success "服务启动命令已执行"
}

# 停止服务
stop_services() {
    log_info "停止远程服务..."
    
    ssh -i "$SSH_KEY" "$SSH_USER@$TARGET_SERVER" "
        echo '🛑 停止PowerAutomation服务...'
        
        # 停止所有相关进程
        pkill -f 'smartui_devops_api_server' 2>/dev/null && echo '✅ SmartUI API Server 已停止' || echo 'ℹ️  SmartUI API Server 未运行'
        pkill -f 'test_manager_mcp_server' 2>/dev/null && echo '✅ Test Manager MCP 已停止' || echo 'ℹ️  Test Manager MCP 未运行'
        pkill -f 'release_manager_mcp_server' 2>/dev/null && echo '✅ Release Manager MCP 已停止' || echo 'ℹ️  Release Manager MCP 未运行'
        pkill -f 'operations_workflow_mcp_server' 2>/dev/null && echo '✅ Operations Workflow MCP 已停止' || echo 'ℹ️  Operations Workflow MCP 未运行'
        
        # 等待进程完全停止
        sleep 3
        
        echo '🎉 所有服务停止完成'
    "
    
    log_success "服务停止命令已执行"
}

# 重启服务
restart_services() {
    log_info "重启远程服务..."
    stop_services
    sleep 5
    start_services
    log_success "服务重启完成"
}

# 查看日志
view_logs() {
    local service=$1
    
    if [ -z "$service" ]; then
        log_info "查看所有服务日志..."
        ssh -i "$SSH_KEY" "$SSH_USER@$TARGET_SERVER" "
            cd $REMOTE_DEPLOY_PATH
            if [ -d 'logs' ]; then
                for log in logs/*.log; do
                    if [ -f \"\$log\" ]; then
                        echo \"=== \$(basename \$log) ===\"
                        tail -20 \"\$log\"
                        echo
                    fi
                done
            else
                echo '⚠️  日志目录不存在'
            fi
        "
    else
        log_info "查看 $service 服务日志..."
        ssh -i "$SSH_KEY" "$SSH_USER@$TARGET_SERVER" "
            cd $REMOTE_DEPLOY_PATH
            if [ -f 'logs/${service}.log' ]; then
                tail -50 'logs/${service}.log'
            else
                echo '⚠️  日志文件不存在: logs/${service}.log'
            fi
        "
    fi
}

# 测试连接
test_connection() {
    log_info "测试服务连接..."
    
    # 测试主API
    if curl -s "http://$TARGET_SERVER:$TARGET_PORT/api/status" > /dev/null; then
        log_success "✅ 主API服务 (端口$TARGET_PORT) 连接正常"
    else
        log_error "❌ 主API服务 (端口$TARGET_PORT) 连接失败"
    fi
    
    # 测试workflow端点
    for service in "Test Manager:8097" "Release Manager:8096" "Operations Workflow:8090"; do
        name=$(echo $service | cut -d: -f1)
        port=$(echo $service | cut -d: -f2)
        
        if curl -s "http://$TARGET_SERVER:$port/api/status" > /dev/null; then
            log_success "✅ $name MCP (端口$port) 连接正常"
        else
            log_error "❌ $name MCP (端口$port) 连接失败"
        fi
    done
}

# 显示帮助信息
show_help() {
    echo "PowerAutomation 远程服务管理工具"
    echo
    echo "用法: $0 [命令] [选项]"
    echo
    echo "命令:"
    echo "  status          查看服务状态"
    echo "  start           启动所有服务"
    echo "  stop            停止所有服务"
    echo "  restart         重启所有服务"
    echo "  logs [service]  查看日志 (可选指定服务名)"
    echo "  test            测试服务连接"
    echo "  help            显示此帮助信息"
    echo
    echo "服务名 (用于logs命令):"
    echo "  smartui_api     SmartUI API Server"
    echo "  test_manager    Test Manager MCP"
    echo "  release_manager Release Manager MCP"
    echo "  operations_workflow Operations Workflow MCP"
    echo
    echo "示例:"
    echo "  $0 status                    # 查看所有服务状态"
    echo "  $0 logs smartui_api         # 查看SmartUI API日志"
    echo "  $0 restart                  # 重启所有服务"
    echo
    echo "服务地址:"
    echo "  主服务: http://$TARGET_SERVER:$TARGET_PORT"
    echo "  Test Manager: http://$TARGET_SERVER:8097"
    echo "  Release Manager: http://$TARGET_SERVER:8096"
    echo "  Operations Workflow: http://$TARGET_SERVER:8090"
}

# 主函数
main() {
    case "$1" in
        "status")
            check_status
            ;;
        "start")
            start_services
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            restart_services
            ;;
        "logs")
            view_logs "$2"
            ;;
        "test")
            test_connection
            ;;
        "help"|"--help"|"-h"|"")
            show_help
            ;;
        *)
            log_error "未知命令: $1"
            echo
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"

