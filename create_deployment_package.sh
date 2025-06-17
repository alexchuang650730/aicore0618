#!/bin/bash

# PowerAutomation 本地打包部署脚本
# 创建完整的部署包，可手动上传到目标服务器

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

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 创建部署包
create_deployment_package() {
    log_info "创建PowerAutomation部署包..."
    
    # 创建部署目录
    DEPLOY_DIR="/tmp/powerautomation_deploy_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$DEPLOY_DIR"
    
    log_info "部署包目录: $DEPLOY_DIR"
    
    # 复制核心文件
    log_info "复制核心文件..."
    
    # 主服务文件
    cp /opt/powerautomation/smartui_devops_api_server_remote.py "$DEPLOY_DIR/smartui_devops_api_server.py"
    cp /opt/powerautomation/smartui_devops_dashboard.html "$DEPLOY_DIR/"
    
    # MCP服务
    mkdir -p "$DEPLOY_DIR/mcp/workflow"
    cp -r /opt/powerautomation/mcp/workflow/test_manager_mcp "$DEPLOY_DIR/mcp/workflow/"
    cp -r /opt/powerautomation/mcp/workflow/release_manager_mcp "$DEPLOY_DIR/mcp/workflow/"
    cp -r /opt/powerautomation/mcp/workflow/operations_workflow_mcp "$DEPLOY_DIR/mcp/workflow/"
    
    # 测试框架
    cp -r /opt/powerautomation/test "$DEPLOY_DIR/"
    
    # 管理脚本
    cp /opt/powerautomation/start_smartui_devops.sh "$DEPLOY_DIR/"
    
    # 创建远程安装脚本
    cat > "$DEPLOY_DIR/install.sh" << 'EOF'
#!/bin/bash

# PowerAutomation 远程安装脚本
# 在目标服务器上运行此脚本完成安装

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

# 检查环境
check_environment() {
    log_info "检查系统环境..."
    
    # 检查Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装，请先安装Python3"
        exit 1
    fi
    
    # 检查pip
    if ! command -v pip3 &> /dev/null; then
        log_error "pip3 未安装，请先安装pip3"
        exit 1
    fi
    
    log_success "环境检查通过"
}

# 安装依赖
install_dependencies() {
    log_info "安装Python依赖..."
    
    pip3 install --user flask flask-cors requests psutil asyncio
    
    log_success "依赖安装完成"
}

# 设置目录和权限
setup_directories() {
    log_info "设置目录和权限..."
    
    # 创建目标目录
    sudo mkdir -p /opt/powerautomation
    sudo chown $USER:$USER /opt/powerautomation
    
    # 复制文件
    cp -r ./* /opt/powerautomation/
    
    # 设置权限
    chmod +x /opt/powerautomation/start_smartui_devops.sh
    chmod +x /opt/powerautomation/install.sh
    
    # 创建日志目录
    mkdir -p /opt/powerautomation/logs
    
    log_success "目录设置完成"
}

# 启动服务
start_services() {
    log_info "启动PowerAutomation服务..."
    
    cd /opt/powerautomation
    
    # 设置Python路径
    export PYTHONPATH=/opt/powerautomation:$PYTHONPATH
    
    # 停止可能存在的服务
    pkill -f 'smartui_devops_api_server' 2>/dev/null || true
    pkill -f 'test_manager_mcp_server' 2>/dev/null || true
    pkill -f 'release_manager_mcp_server' 2>/dev/null || true
    pkill -f 'operations_workflow_mcp_server' 2>/dev/null || true
    
    sleep 3
    
    # 启动Test Manager MCP
    if [ -f 'mcp/workflow/test_manager_mcp/test_manager_mcp_server.py' ]; then
        nohup python3 mcp/workflow/test_manager_mcp/test_manager_mcp_server.py > logs/test_manager.log 2>&1 &
        log_success "Test Manager MCP 启动"
        sleep 2
    fi
    
    # 启动Release Manager MCP
    if [ -f 'mcp/workflow/release_manager_mcp/release_manager_mcp_server.py' ]; then
        nohup python3 mcp/workflow/release_manager_mcp/release_manager_mcp_server.py > logs/release_manager.log 2>&1 &
        log_success "Release Manager MCP 启动"
        sleep 2
    fi
    
    # 启动Operations Workflow MCP
    if [ -f 'mcp/workflow/operations_workflow_mcp/operations_workflow_mcp_server.py' ]; then
        nohup python3 mcp/workflow/operations_workflow_mcp/operations_workflow_mcp_server.py > logs/operations_workflow.log 2>&1 &
        log_success "Operations Workflow MCP 启动"
        sleep 2
    fi
    
    # 启动主API服务器
    if [ -f 'smartui_devops_api_server.py' ]; then
        nohup python3 smartui_devops_api_server.py > logs/smartui_api.log 2>&1 &
        log_success "SmartUI API Server 启动"
        sleep 3
    fi
    
    log_success "所有服务启动完成"
}

# 验证安装
verify_installation() {
    log_info "验证安装..."
    
    sleep 5
    
    # 检查进程
    echo "=== 服务进程 ==="
    ps aux | grep -E '(smartui_devops|test_manager|release_manager|operations_workflow)' | grep -v grep || echo "警告: 某些服务可能未启动"
    
    echo
    echo "=== 端口监听 ==="
    netstat -tlnp 2>/dev/null | grep -E ':(5001|8090|8096|8097)' || echo "警告: 某些端口未监听"
    
    echo
    echo "=== 服务测试 ==="
    
    # 测试主API
    if curl -s http://localhost:5001/api/status > /dev/null; then
        log_success "主API服务 (端口5001) 正常"
    else
        log_error "主API服务 (端口5001) 异常"
    fi
    
    # 测试MCP服务
    for service in "Test Manager:8097" "Release Manager:8096" "Operations Workflow:8090"; do
        name=$(echo $service | cut -d: -f1)
        port=$(echo $service | cut -d: -f2)
        
        if curl -s "http://localhost:$port/api/status" > /dev/null; then
            log_success "$name MCP (端口$port) 正常"
        else
            log_error "$name MCP (端口$port) 异常"
        fi
    done
}

# 显示完成信息
show_completion_info() {
    log_success "🎉 PowerAutomation安装完成！"
    echo
    echo "=================================="
    echo "📍 服务信息"
    echo "=================================="
    echo "🌐 主服务地址: http://$(hostname -I | awk '{print $1}'):5001"
    echo "📊 API状态: http://$(hostname -I | awk '{print $1}'):5001/api/status"
    echo "🔧 Workflow状态: http://$(hostname -I | awk '{print $1}'):5001/api/workflows/status"
    echo
    echo "🛠️ Workflow MCP端点:"
    echo "   • Test Manager: http://$(hostname -I | awk '{print $1}'):8097"
    echo "   • Release Manager: http://$(hostname -I | awk '{print $1}'):8096"
    echo "   • Operations Workflow: http://$(hostname -I | awk '{print $1}'):8090"
    echo
    echo "📁 安装路径: /opt/powerautomation"
    echo "📝 日志路径: /opt/powerautomation/logs"
    echo
    echo "🔧 管理命令:"
    echo "   查看服务状态: ps aux | grep smartui"
    echo "   查看日志: tail -f /opt/powerautomation/logs/*.log"
    echo "   重启服务: cd /opt/powerautomation && ./start_smartui_devops.sh"
    echo
    echo "✅ 安装成功完成！"
}

# 主函数
main() {
    echo "🚀 开始PowerAutomation安装..."
    echo "=================================="
    
    check_environment
    install_dependencies
    setup_directories
    start_services
    verify_installation
    show_completion_info
}

# 错误处理
trap 'log_error "安装过程中发生错误，请检查日志"; exit 1' ERR

# 执行主函数
main "$@"
EOF
    
    chmod +x "$DEPLOY_DIR/install.sh"
    
    # 创建README文件
    cat > "$DEPLOY_DIR/README.md" << 'EOF'
# PowerAutomation 部署包

## 快速安装

1. 将此目录上传到目标服务器 98.81.255.168
2. 在服务器上运行安装脚本：
   ```bash
   chmod +x install.sh
   ./install.sh
   ```

## 服务地址

安装完成后，访问以下地址：
- 主界面: http://98.81.255.168:5001
- API状态: http://98.81.255.168:5001/api/status

## 文件说明

- `smartui_devops_api_server.py` - 主API服务器
- `smartui_devops_dashboard.html` - Web界面
- `mcp/workflow/` - 三个Workflow MCP服务
- `test/` - 测试框架
- `install.sh` - 自动安装脚本
- `start_smartui_devops.sh` - 服务启动脚本

## 系统要求

- Ubuntu 18.04+ 或 CentOS 7+
- Python 3.6+
- pip3
- 网络连接

## 端口要求

确保以下端口开放：
- 5001 (主服务)
- 8090 (Operations Workflow MCP)
- 8096 (Release Manager MCP)
- 8097 (Test Manager MCP)
EOF
    
    # 创建压缩包
    cd /tmp
    tar -czf "powerautomation_deploy_$(date +%Y%m%d_%H%M%S).tar.gz" "$(basename $DEPLOY_DIR)"
    
    log_success "部署包创建完成！"
    echo
    echo "=================================="
    echo "📦 部署包信息"
    echo "=================================="
    echo "📁 部署目录: $DEPLOY_DIR"
    echo "📦 压缩包: /tmp/powerautomation_deploy_$(date +%Y%m%d_%H%M%S).tar.gz"
    echo
    echo "🚀 部署步骤:"
    echo "1. 将部署包上传到 98.81.255.168"
    echo "2. 解压: tar -xzf powerautomation_deploy_*.tar.gz"
    echo "3. 进入目录: cd powerautomation_deploy_*"
    echo "4. 运行安装: ./install.sh"
    echo
    echo "✅ 部署包准备完成！"
    
    return 0
}

# 主函数
main() {
    echo "🚀 创建PowerAutomation部署包..."
    echo "=================================="
    
    create_deployment_package
}

# 执行主函数
main "$@"

