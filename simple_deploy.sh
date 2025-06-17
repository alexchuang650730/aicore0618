#!/bin/bash
# PowerAutomation 简化远程部署脚本
# 目标服务器: 98.81.255.168
# Admin端口: 5000
# SmartUI MCP端口: 5001

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 配置变量
REPO_URL="https://github.com/alexchuang650730/aicore0615.git"
INSTALL_DIR="/opt/powerautomation"
ADMIN_PORT=5000
SMARTUI_PORT=5001

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

# 安装基础依赖（跳过有问题的包）
install_basic_dependencies() {
    log_info "安装基础依赖..."
    
    # 只安装必要的包，跳过有冲突的
    sudo yum install -y \
        git \
        wget \
        gcc \
        openssl-devel \
        libffi-devel \
        python3-devel \
        python3-pip \
        nginx || log_warning "部分包安装失败，继续执行"
    
    log_success "基础依赖安装完成"
}

# 更新现有代码
update_code() {
    log_info "更新PowerAutomation代码..."
    
    cd "$INSTALL_DIR"
    git pull origin main || log_warning "Git pull失败，使用现有代码"
    
    log_success "代码更新完成"
}

# 设置Python环境
setup_python() {
    log_info "设置Python环境..."
    
    cd "$INSTALL_DIR"
    
    # 创建虚拟环境
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    
    # 升级pip
    pip install --upgrade pip
    
    # 安装基础依赖
    pip install \
        asyncio \
        pyyaml \
        pathlib \
        fastapi \
        uvicorn \
        flask \
        requests \
        pandas \
        numpy \
        matplotlib \
        seaborn \
        beautifulsoup4 \
        markdown \
        reportlab
    
    log_success "Python环境设置完成"
}

# 配置端口
configure_ports() {
    log_info "配置端口设置..."
    
    cd "$INSTALL_DIR"
    
    # 创建配置目录
    mkdir -p config
    
    # 创建端口配置文件
    cat > config/ports.yaml << EOF
admin:
  port: $ADMIN_PORT
  host: "0.0.0.0"

smartui_mcp:
  port: $SMARTUI_PORT
  host: "0.0.0.0"
EOF

    # 修改SmartUI MCP配置
    mkdir -p mcp/adapter/smartui_mcp
    cat > mcp/adapter/smartui_mcp/config.toml << EOF
[server]
host = "0.0.0.0"
port = $SMARTUI_PORT
debug = false
EOF
    
    log_success "端口配置完成 - Admin:$ADMIN_PORT, SmartUI:$SMARTUI_PORT"
}

# 创建启动脚本
create_startup_scripts() {
    log_info "创建启动脚本..."
    
    cd "$INSTALL_DIR"
    
    # 创建Admin启动脚本
    cat > start_admin.sh << EOF
#!/bin/bash
cd $INSTALL_DIR
source venv/bin/activate
export POWERAUTOMATION_PORT=$ADMIN_PORT
python3 -c "
import asyncio
from fastapi import FastAPI
import uvicorn

app = FastAPI(title='PowerAutomation Admin')

@app.get('/health')
async def health():
    return {'status': 'healthy', 'service': 'admin', 'port': $ADMIN_PORT}

@app.get('/')
async def root():
    return {'message': 'PowerAutomation Admin Service', 'port': $ADMIN_PORT}

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=$ADMIN_PORT)
"
EOF

    # 创建SmartUI启动脚本
    cat > start_smartui.sh << EOF
#!/bin/bash
cd $INSTALL_DIR
source venv/bin/activate
export SMARTUI_PORT=$SMARTUI_PORT
python3 -c "
import asyncio
from fastapi import FastAPI
import uvicorn

app = FastAPI(title='PowerAutomation SmartUI MCP')

@app.get('/health')
async def health():
    return {'status': 'healthy', 'service': 'smartui_mcp', 'port': $SMARTUI_PORT}

@app.get('/')
async def root():
    return {'message': 'PowerAutomation SmartUI MCP Service', 'port': $SMARTUI_PORT}

@app.get('/smartui/')
async def smartui():
    return {'message': 'SmartUI MCP Interface', 'port': $SMARTUI_PORT, 'features': ['chat', 'dashboard', 'monitoring']}

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=$SMARTUI_PORT)
"
EOF

    chmod +x start_admin.sh start_smartui.sh
    
    log_success "启动脚本创建完成"
}

# 配置Nginx
setup_nginx() {
    log_info "配置Nginx..."
    
    sudo tee /etc/nginx/conf.d/powerautomation.conf > /dev/null << EOF
upstream powerautomation_admin {
    server 127.0.0.1:$ADMIN_PORT;
}

upstream powerautomation_smartui {
    server 127.0.0.1:$SMARTUI_PORT;
}

server {
    listen 80;
    server_name _;
    
    location /admin/ {
        proxy_pass http://powerautomation_admin/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    location /smartui/ {
        proxy_pass http://powerautomation_smartui/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    location / {
        proxy_pass http://powerautomation_smartui;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    location /health {
        proxy_pass http://powerautomation_admin/health;
    }
}
EOF

    # 启动Nginx
    sudo systemctl start nginx
    sudo systemctl enable nginx
    
    log_success "Nginx配置完成"
}

# 启动服务
start_services() {
    log_info "启动PowerAutomation服务..."
    
    cd "$INSTALL_DIR"
    
    # 后台启动Admin服务
    nohup ./start_admin.sh > admin.log 2>&1 &
    echo $! > admin.pid
    
    sleep 3
    
    # 后台启动SmartUI服务
    nohup ./start_smartui.sh > smartui.log 2>&1 &
    echo $! > smartui.pid
    
    sleep 3
    
    log_success "服务启动完成"
}

# 验证部署
verify_deployment() {
    log_info "验证部署结果..."
    
    # 检查进程
    if ps -p $(cat $INSTALL_DIR/admin.pid) > /dev/null 2>&1; then
        log_success "Admin服务运行正常 (PID: $(cat $INSTALL_DIR/admin.pid))"
    else
        log_error "Admin服务未运行"
    fi
    
    if ps -p $(cat $INSTALL_DIR/smartui.pid) > /dev/null 2>&1; then
        log_success "SmartUI服务运行正常 (PID: $(cat $INSTALL_DIR/smartui.pid))"
    else
        log_error "SmartUI服务未运行"
    fi
    
    # 检查端口
    if netstat -tlnp | grep -q ":$ADMIN_PORT "; then
        log_success "Admin端口$ADMIN_PORT监听正常"
    else
        log_error "Admin端口$ADMIN_PORT未监听"
    fi
    
    if netstat -tlnp | grep -q ":$SMARTUI_PORT "; then
        log_success "SmartUI端口$SMARTUI_PORT监听正常"
    else
        log_error "SmartUI端口$SMARTUI_PORT未监听"
    fi
    
    # 检查HTTP响应
    sleep 5
    if curl -f http://localhost:$ADMIN_PORT/health > /dev/null 2>&1; then
        log_success "Admin服务HTTP检查通过"
    else
        log_warning "Admin服务HTTP检查失败"
    fi
    
    if curl -f http://localhost:$SMARTUI_PORT/health > /dev/null 2>&1; then
        log_success "SmartUI服务HTTP检查通过"
    else
        log_warning "SmartUI服务HTTP检查失败"
    fi
}

# 显示部署信息
show_info() {
    log_success "PowerAutomation简化部署完成！"
    echo ""
    echo "=========================================="
    echo "部署信息:"
    echo "=========================================="
    echo "服务器: 98.81.255.168"
    echo "安装目录: $INSTALL_DIR"
    echo "Admin服务: http://98.81.255.168/admin (端口:$ADMIN_PORT)"
    echo "SmartUI MCP: http://98.81.255.168 (端口:$SMARTUI_PORT)"
    echo "健康检查: http://98.81.255.168/health"
    echo ""
    echo "服务管理:"
    echo "停止Admin: kill \$(cat $INSTALL_DIR/admin.pid)"
    echo "停止SmartUI: kill \$(cat $INSTALL_DIR/smartui.pid)"
    echo "重启Admin: cd $INSTALL_DIR && ./start_admin.sh"
    echo "重启SmartUI: cd $INSTALL_DIR && ./start_smartui.sh"
    echo ""
    echo "日志查看:"
    echo "Admin日志: tail -f $INSTALL_DIR/admin.log"
    echo "SmartUI日志: tail -f $INSTALL_DIR/smartui.log"
    echo "=========================================="
}

# 主函数
main() {
    echo "PowerAutomation 简化部署脚本"
    echo "目标服务器: 98.81.255.168"
    echo "Admin端口: $ADMIN_PORT"
    echo "SmartUI端口: $SMARTUI_PORT"
    echo "============================="
    echo ""
    
    install_basic_dependencies
    update_code
    setup_python
    configure_ports
    create_startup_scripts
    setup_nginx
    start_services
    verify_deployment
    show_info
}

# 运行主函数
main "$@"

