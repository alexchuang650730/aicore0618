#!/bin/bash

# PowerAutomation 远程部署脚本
# 目标服务器: 98.81.255.168:5001
# 作者: PowerAutomation Team
# 版本: 3.0.0

set -e  # 遇到错误立即退出

# 加载配置
source /opt/powerautomation/deploy_config.sh

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
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

# 检查本地环境
check_local_environment() {
    log_info "检查本地部署环境..."
    
    # 检查SSH密钥
    if [ ! -f "$SSH_KEY" ]; then
        log_error "SSH密钥文件不存在: $SSH_KEY"
        exit 1
    fi
    
    # 检查必要文件
    for file in "${REQUIRED_FILES[@]}"; do
        if [ ! -e "/opt/powerautomation/$file" ]; then
            log_error "必要文件缺失: $file"
            exit 1
        fi
    done
    
    log_success "本地环境检查通过"
}

# 测试SSH连接
test_ssh_connection() {
    log_info "测试SSH连接到 $TARGET_SERVER..."
    
    # 尝试多种SSH连接方式
    SSH_OPTIONS="-o ConnectTimeout=30 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR"
    
    # 方式1: 标准连接
    if ssh -i "$SSH_KEY" $SSH_OPTIONS "$SSH_USER@$TARGET_SERVER" "echo 'SSH连接成功'" 2>/dev/null; then
        log_success "SSH连接测试成功"
        return 0
    fi
    
    # 方式2: 尝试不同端口
    for port in 22 2222 22222; do
        log_info "尝试端口 $port..."
        if ssh -i "$SSH_KEY" -p $port $SSH_OPTIONS "$SSH_USER@$TARGET_SERVER" "echo 'SSH连接成功'" 2>/dev/null; then
            log_success "SSH连接成功 (端口 $port)"
            # 更新SSH配置
            SSH_PORT=$port
            return 0
        fi
    done
    
    # 方式3: 尝试不同用户名
    for user in ubuntu root ec2-user admin; do
        if [ "$user" != "$SSH_USER" ]; then
            log_info "尝试用户 $user..."
            if ssh -i "$SSH_KEY" $SSH_OPTIONS "$user@$TARGET_SERVER" "echo 'SSH连接成功'" 2>/dev/null; then
                log_success "SSH连接成功 (用户 $user)"
                SSH_USER=$user
                return 0
            fi
        fi
    done
    
    # 方式4: 详细调试信息
    log_warning "标准连接失败，显示详细调试信息..."
    ssh -i "$SSH_KEY" -v -o ConnectTimeout=10 -o StrictHostKeyChecking=no "$SSH_USER@$TARGET_SERVER" "echo 'SSH连接成功'" 2>&1 | head -20
    
    log_error "SSH连接失败，请检查:"
    log_error "1. 服务器地址: $TARGET_SERVER"
    log_error "2. SSH密钥: $SSH_KEY"
    log_error "3. 用户名: $SSH_USER"
    log_error "4. 网络连接"
    log_error "5. SSH服务是否运行"
    log_error "6. 防火墙设置"
    
    # 提供手动部署选项
    log_info "您可以选择:"
    log_info "1. 检查SSH配置后重试"
    log_info "2. 使用手动部署包: /tmp/powerautomation_deploy_*.tar.gz"
    
    return 1
}

# 检查远程环境
check_remote_environment() {
    log_info "检查远程服务器环境..."
    
    # 检查系统要求
    ssh -i "$SSH_KEY" ${SSH_PORT:+-p $SSH_PORT} "$SSH_USER@$TARGET_SERVER" "
        # 检查Python
        if ! command -v python3 &> /dev/null; then
            echo 'ERROR: Python3 未安装'
            exit 1
        fi
        
        # 检查pip
        if ! command -v pip3 &> /dev/null; then
            echo 'ERROR: pip3 未安装'
            exit 1
        fi
        
        # 检查curl
        if ! command -v curl &> /dev/null; then
            echo 'ERROR: curl 未安装'
            exit 1
        fi
        
        echo 'SUCCESS: 远程环境检查通过'
    "
    
    if [ $? -eq 0 ]; then
        log_success "远程环境检查通过"
    else
        log_error "远程环境检查失败"
        exit 1
    fi
}

# 创建远程目录结构
create_remote_directories() {
    log_info "创建远程目录结构..."
    
    ssh -i "$SSH_KEY" "$SSH_USER@$TARGET_SERVER" "
        # 创建主目录
        sudo mkdir -p $REMOTE_DEPLOY_PATH
        sudo chown $SSH_USER:$SSH_USER $REMOTE_DEPLOY_PATH
        
        # 创建备份目录
        sudo mkdir -p $REMOTE_BACKUP_PATH
        sudo chown $SSH_USER:$SSH_USER $REMOTE_BACKUP_PATH
        
        # 创建子目录
        mkdir -p $REMOTE_DEPLOY_PATH/mcp/workflow/test_manager_mcp
        mkdir -p $REMOTE_DEPLOY_PATH/mcp/workflow/release_manager_mcp
        mkdir -p $REMOTE_DEPLOY_PATH/mcp/workflow/operations_workflow_mcp
        mkdir -p $REMOTE_DEPLOY_PATH/test/framework
        mkdir -p $REMOTE_DEPLOY_PATH/logs
        
        echo 'SUCCESS: 目录结构创建完成'
    "
    
    log_success "远程目录结构创建完成"
}

# 备份现有部署
backup_existing_deployment() {
    log_info "备份现有部署..."
    
    ssh -i "$SSH_KEY" "$SSH_USER@$TARGET_SERVER" "
        if [ -d '$REMOTE_DEPLOY_PATH' ]; then
            BACKUP_NAME='powerautomation_backup_\$(date +%Y%m%d_%H%M%S)'
            cp -r $REMOTE_DEPLOY_PATH $REMOTE_BACKUP_PATH/\$BACKUP_NAME
            echo \"SUCCESS: 备份创建完成: \$BACKUP_NAME\"
        else
            echo 'INFO: 无现有部署需要备份'
        fi
    "
    
    log_success "备份操作完成"
}

# 上传文件
upload_files() {
    log_info "上传项目文件..."
    
    # 上传主要文件
    scp -i "$SSH_KEY" -r /opt/powerautomation/smartui_devops_api_server_remote.py "$SSH_USER@$TARGET_SERVER:$REMOTE_DEPLOY_PATH/smartui_devops_api_server.py"
    scp -i "$SSH_KEY" -r /opt/powerautomation/smartui_devops_dashboard.html "$SSH_USER@$TARGET_SERVER:$REMOTE_DEPLOY_PATH/"
    
    # 上传MCP文件
    scp -i "$SSH_KEY" -r /opt/powerautomation/mcp/workflow/test_manager_mcp/ "$SSH_USER@$TARGET_SERVER:$REMOTE_DEPLOY_PATH/mcp/workflow/"
    scp -i "$SSH_KEY" -r /opt/powerautomation/mcp/workflow/release_manager_mcp/ "$SSH_USER@$TARGET_SERVER:$REMOTE_DEPLOY_PATH/mcp/workflow/"
    scp -i "$SSH_KEY" -r /opt/powerautomation/mcp/workflow/operations_workflow_mcp/ "$SSH_USER@$TARGET_SERVER:$REMOTE_DEPLOY_PATH/mcp/workflow/"
    
    # 上传测试框架
    scp -i "$SSH_KEY" -r /opt/powerautomation/test/ "$SSH_USER@$TARGET_SERVER:$REMOTE_DEPLOY_PATH/"
    
    # 上传启动脚本
    scp -i "$SSH_KEY" -r /opt/powerautomation/start_smartui_devops.sh "$SSH_USER@$TARGET_SERVER:$REMOTE_DEPLOY_PATH/"
    
    log_success "文件上传完成"
}

# 安装Python依赖
install_dependencies() {
    log_info "安装Python依赖..."
    
    ssh -i "$SSH_KEY" "$SSH_USER@$TARGET_SERVER" "
        cd $REMOTE_DEPLOY_PATH
        
        # 安装Python包
        pip3 install --user $PYTHON_REQUIREMENTS
        
        # 设置权限
        chmod +x start_smartui_devops.sh
        chmod +x mcp/workflow/*/test_manager_mcp_server.py 2>/dev/null || true
        chmod +x mcp/workflow/*/release_manager_mcp_server.py 2>/dev/null || true
        chmod +x mcp/workflow/*/operations_workflow_mcp_server.py 2>/dev/null || true
        
        echo 'SUCCESS: 依赖安装完成'
    "
    
    log_success "Python依赖安装完成"
}

# 停止现有服务
stop_existing_services() {
    log_info "停止现有服务..."
    
    ssh -i "$SSH_KEY" "$SSH_USER@$TARGET_SERVER" "
        # 停止可能运行的服务
        pkill -f 'smartui_devops_api_server' 2>/dev/null || true
        pkill -f 'test_manager_mcp_server' 2>/dev/null || true
        pkill -f 'release_manager_mcp_server' 2>/dev/null || true
        pkill -f 'operations_workflow_mcp_server' 2>/dev/null || true
        
        # 等待进程完全停止
        sleep 3
        
        echo 'SUCCESS: 现有服务已停止'
    "
    
    log_success "现有服务停止完成"
}

# 启动服务
start_services() {
    log_info "启动PowerAutomation服务..."
    
    ssh -i "$SSH_KEY" "$SSH_USER@$TARGET_SERVER" "
        cd $REMOTE_DEPLOY_PATH
        
        # 设置Python路径
        export PYTHONPATH=$REMOTE_DEPLOY_PATH:\$PYTHONPATH
        
        # 启动Test Manager MCP
        nohup python3 mcp/workflow/test_manager_mcp/test_manager_mcp_server.py > logs/test_manager.log 2>&1 &
        sleep 2
        
        # 启动Release Manager MCP
        nohup python3 mcp/workflow/release_manager_mcp/release_manager_mcp_server.py > logs/release_manager.log 2>&1 &
        sleep 2
        
        # 启动Operations Workflow MCP
        nohup python3 mcp/workflow/operations_workflow_mcp/operations_workflow_mcp_server.py > logs/operations_workflow.log 2>&1 &
        sleep 2
        
        # 启动主API服务器
        nohup python3 smartui_devops_api_server.py > logs/smartui_api.log 2>&1 &
        sleep 3
        
        echo 'SUCCESS: 所有服务启动完成'
    "
    
    log_success "服务启动完成"
}

# 验证部署
verify_deployment() {
    log_info "验证部署状态..."
    
    # 等待服务完全启动
    sleep 10
    
    # 检查服务状态
    ssh -i "$SSH_KEY" "$SSH_USER@$TARGET_SERVER" "
        cd $REMOTE_DEPLOY_PATH
        
        # 检查进程
        echo '=== 检查服务进程 ==='
        ps aux | grep -E '(smartui_devops|test_manager|release_manager|operations_workflow)' | grep -v grep || echo '警告: 某些服务可能未启动'
        
        echo
        echo '=== 检查端口占用 ==='
        netstat -tlnp 2>/dev/null | grep -E ':(5001|8090|8096|8097)' || echo '警告: 某些端口未监听'
        
        echo
        echo '=== 检查日志文件 ==='
        ls -la logs/ 2>/dev/null || echo '警告: 日志目录不存在'
    "
    
    # 测试API端点
    log_info "测试API端点..."
    
    # 测试主API
    if curl -s "http://$TARGET_SERVER:$TARGET_PORT/api/status" > /dev/null; then
        log_success "主API服务响应正常"
    else
        log_warning "主API服务可能未完全启动"
    fi
    
    # 测试workflow端点
    for service in "test_manager:8097" "release_manager:8096" "operations_workflow:8090"; do
        name=$(echo $service | cut -d: -f1)
        port=$(echo $service | cut -d: -f2)
        
        if curl -s "http://$TARGET_SERVER:$port/api/status" > /dev/null; then
            log_success "$name MCP服务响应正常"
        else
            log_warning "$name MCP服务可能未完全启动"
        fi
    done
}

# 显示部署信息
show_deployment_info() {
    log_success "🎉 PowerAutomation远程部署完成！"
    echo
    echo "=================================="
    echo "📍 部署信息"
    echo "=================================="
    echo "🌐 主服务地址: http://$TARGET_SERVER:$TARGET_PORT"
    echo "📊 API状态: http://$TARGET_SERVER:$TARGET_PORT/api/status"
    echo "🔧 Workflow状态: http://$TARGET_SERVER:$TARGET_PORT/api/workflows/status"
    echo
    echo "🛠️ Workflow MCP端点:"
    echo "   • Test Manager: http://$TARGET_SERVER:8097"
    echo "   • Release Manager: http://$TARGET_SERVER:8096"
    echo "   • Operations Workflow: http://$TARGET_SERVER:8090"
    echo
    echo "📁 远程部署路径: $REMOTE_DEPLOY_PATH"
    echo "💾 备份路径: $REMOTE_BACKUP_PATH"
    echo
    echo "🔧 管理命令:"
    echo "   查看服务状态: ssh -i $SSH_KEY $SSH_USER@$TARGET_SERVER 'ps aux | grep smartui'"
    echo "   查看日志: ssh -i $SSH_KEY $SSH_USER@$TARGET_SERVER 'tail -f $REMOTE_DEPLOY_PATH/logs/*.log'"
    echo "   重启服务: ssh -i $SSH_KEY $SSH_USER@$TARGET_SERVER 'cd $REMOTE_DEPLOY_PATH && ./start_smartui_devops.sh'"
    echo
    echo "✅ 部署成功完成！"
}

# 主函数
main() {
    echo "🚀 开始PowerAutomation远程部署..."
    echo "目标服务器: $TARGET_SERVER:$TARGET_PORT"
    echo "=================================="
    
    check_local_environment
    test_ssh_connection
    check_remote_environment
    create_remote_directories
    backup_existing_deployment
    upload_files
    install_dependencies
    stop_existing_services
    start_services
    verify_deployment
    show_deployment_info
}

# 错误处理
trap 'log_error "部署过程中发生错误，请检查日志"; exit 1' ERR

# 执行主函数
main "$@"

