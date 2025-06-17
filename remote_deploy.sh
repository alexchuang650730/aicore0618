#!/bin/bash
# PowerAutomation 远程部署脚本
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
SERVICE_USER="ec2-user"

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

# 检查系统环境
check_system() {
    log_info "检查系统环境..."
    
    # 检查操作系统
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        log_info "操作系统: $NAME $VERSION_ID"
    fi
    
    # 检查内存
    MEMORY_GB=$(free -g | awk '/^Mem:/{print $2}')
    log_info "系统内存: ${MEMORY_GB}GB"
    
    # 检查磁盘空间
    DISK_SPACE=$(df -BG /opt | awk 'NR==2 {print $4}' | sed 's/G//')
    log_info "可用磁盘空间: ${DISK_SPACE}GB"
    
    if [ $DISK_SPACE -lt 5 ]; then
        log_error "磁盘空间不足，至少需要5GB"
        exit 1
    fi
}

# 安装系统依赖
install_dependencies() {
    log_info "安装系统依赖..."
    
    # 更新包管理器
    if command -v yum &> /dev/null; then
        sudo yum update -y
        sudo yum install -y \
            git \
            curl \
            wget \
            gcc \
            openssl-devel \
            libffi-devel \
            python3-devel \
            python3-pip \
            postgresql15-server \
            postgresql15 \
            redis6 \
            nginx
    elif command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y \
            git \
            curl \
            wget \
            build-essential \
            libssl-dev \
            libffi-dev \
            python3-dev \
            python3-pip \
            python3-venv \
            postgresql \
            redis-server \
            nginx
    else
        log_error "不支持的包管理器"
        exit 1
    fi
    
    log_success "系统依赖安装完成"
}

# 克隆或更新代码
setup_code() {
    log_info "设置PowerAutomation代码..."
    
    if [ -d "$INSTALL_DIR/.git" ]; then
        log_info "更新现有代码仓库..."
        cd "$INSTALL_DIR"
        git pull origin main
    else
        log_info "克隆PowerAutomation代码仓库..."
        if [ -d "$INSTALL_DIR" ]; then
            sudo rm -rf "$INSTALL_DIR"
        fi
        sudo mkdir -p "$INSTALL_DIR"
        sudo chown $SERVICE_USER:$SERVICE_USER "$INSTALL_DIR"
        git clone "$REPO_URL" "$INSTALL_DIR"
    fi
    
    cd "$INSTALL_DIR"
    log_success "代码设置完成"
}

# 创建Python虚拟环境
setup_python_env() {
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
        reportlab \
        psycopg2-binary \
        redis \
        python-multipart \
        jinja2
    
    log_success "Python环境设置完成"
}

# 配置端口设置
configure_ports() {
    log_info "配置端口设置..."
    
    cd "$INSTALL_DIR"
    
    # 创建端口配置文件
    cat > config/ports.yaml << EOF
# PowerAutomation 端口配置
admin:
  port: $ADMIN_PORT
  host: "0.0.0.0"
  description: "管理后台端口"

smartui_mcp:
  port: $SMARTUI_PORT
  host: "0.0.0.0"
  description: "SmartUI MCP服务端口"

services:
  coordinator: 8000
  database: 5432
  redis: 6379
  nginx: 80
EOF

    # 修改SmartUI MCP配置
    if [ -f "mcp/adapter/smartui_mcp/config.toml" ]; then
        sed -i "s/port = .*/port = $SMARTUI_PORT/" mcp/adapter/smartui_mcp/config.toml
    else
        mkdir -p mcp/adapter/smartui_mcp
        cat > mcp/adapter/smartui_mcp/config.toml << EOF
[server]
host = "0.0.0.0"
port = $SMARTUI_PORT
debug = false

[database]
url = "postgresql://powerautomation:powerautomation@localhost:5432/powerautomation"

[cache]
redis_url = "redis://localhost:6379/0"
EOF
    fi
    
    # 修改主配置文件
    cat > config/production.yaml << EOF
# PowerAutomation 生产环境配置
server:
  admin_port: $ADMIN_PORT
  smartui_port: $SMARTUI_PORT
  host: "0.0.0.0"
  workers: 4

database:
  url: "postgresql://powerautomation:powerautomation@localhost:5432/powerautomation"
  pool_size: 20
  max_overflow: 30

cache:
  redis_url: "redis://localhost:6379/0"
  default_timeout: 3600

security:
  secret_key: "$(openssl rand -hex 32)"
  jwt_expiry: 3600

logging:
  level: "INFO"
  format: "json"
  file: "/var/log/powerautomation/app.log"

features:
  smartui_mcp: true
  enhanced_workflow: true
  test_framework: true
  monitoring: true
EOF
    
    log_success "端口配置完成 - Admin:$ADMIN_PORT, SmartUI:$SMARTUI_PORT"
}

# 配置数据库
setup_database() {
    log_info "配置PostgreSQL数据库..."
    
    # 启动PostgreSQL
    if command -v systemctl &> /dev/null; then
        sudo systemctl start postgresql
        sudo systemctl enable postgresql
    fi
    
    # 创建数据库和用户
    sudo -u postgres psql -c "CREATE DATABASE powerautomation;" 2>/dev/null || log_warning "数据库可能已存在"
    sudo -u postgres psql -c "CREATE USER powerautomation WITH PASSWORD 'powerautomation';" 2>/dev/null || log_warning "用户可能已存在"
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE powerautomation TO powerautomation;" 2>/dev/null
    
    log_success "数据库配置完成"
}

# 配置Redis
setup_redis() {
    log_info "配置Redis..."
    
    # 启动Redis
    if command -v systemctl &> /dev/null; then
        sudo systemctl start redis
        sudo systemctl enable redis
    fi
    
    # 测试Redis连接
    if redis-cli ping | grep -q "PONG"; then
        log_success "Redis配置完成"
    else
        log_error "Redis连接失败"
        exit 1
    fi
}

# 创建系统服务
create_services() {
    log_info "创建系统服务..."
    
    # 创建Admin服务
    sudo tee /etc/systemd/system/powerautomation-admin.service > /dev/null << EOF
[Unit]
Description=PowerAutomation Admin Service
After=network.target postgresql.service redis.service
Wants=postgresql.service redis.service

[Service]
Type=simple
User=$SERVICE_USER
Group=$SERVICE_USER
WorkingDirectory=$INSTALL_DIR
Environment=PATH=$INSTALL_DIR/venv/bin
Environment=POWERAUTOMATION_PORT=$ADMIN_PORT
ExecStart=$INSTALL_DIR/venv/bin/python main.py --port $ADMIN_PORT
ExecReload=/bin/kill -HUP \$MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    # 创建SmartUI MCP服务
    sudo tee /etc/systemd/system/powerautomation-smartui.service > /dev/null << EOF
[Unit]
Description=PowerAutomation SmartUI MCP Service
After=network.target postgresql.service redis.service
Wants=postgresql.service redis.service

[Service]
Type=simple
User=$SERVICE_USER
Group=$SERVICE_USER
WorkingDirectory=$INSTALL_DIR/mcp/adapter/smartui_mcp
Environment=PATH=$INSTALL_DIR/venv/bin
Environment=SMARTUI_PORT=$SMARTUI_PORT
ExecStart=$INSTALL_DIR/venv/bin/python cli.py start --port $SMARTUI_PORT
ExecReload=/bin/kill -HUP \$MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable powerautomation-admin
    sudo systemctl enable powerautomation-smartui
    
    log_success "系统服务创建完成"
}

# 配置Nginx
setup_nginx() {
    log_info "配置Nginx反向代理..."
    
    sudo tee /etc/nginx/conf.d/powerautomation.conf > /dev/null << EOF
# PowerAutomation Nginx配置
upstream powerautomation_admin {
    server 127.0.0.1:$ADMIN_PORT;
}

upstream powerautomation_smartui {
    server 127.0.0.1:$SMARTUI_PORT;
}

server {
    listen 80;
    server_name _;
    
    # Admin后台
    location /admin/ {
        proxy_pass http://powerautomation_admin/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # SmartUI MCP
    location /smartui/ {
        proxy_pass http://powerautomation_smartui/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # 默认路由到SmartUI
    location / {
        proxy_pass http://powerautomation_smartui;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # 健康检查
    location /health {
        access_log off;
        proxy_pass http://powerautomation_admin/health;
    }
    
    # 静态文件
    location /static/ {
        alias $INSTALL_DIR/static/;
        expires 30d;
    }
}
EOF

    # 测试Nginx配置
    sudo nginx -t
    
    # 启动Nginx
    sudo systemctl start nginx
    sudo systemctl enable nginx
    
    log_success "Nginx配置完成"
}

# 配置防火墙
setup_firewall() {
    log_info "配置防火墙..."
    
    # 检查防火墙类型
    if command -v firewall-cmd &> /dev/null; then
        # CentOS/RHEL firewalld
        sudo firewall-cmd --permanent --add-port=80/tcp
        sudo firewall-cmd --permanent --add-port=443/tcp
        sudo firewall-cmd --permanent --add-port=$ADMIN_PORT/tcp
        sudo firewall-cmd --permanent --add-port=$SMARTUI_PORT/tcp
        sudo firewall-cmd --reload
    elif command -v ufw &> /dev/null; then
        # Ubuntu UFW
        sudo ufw allow 80/tcp
        sudo ufw allow 443/tcp
        sudo ufw allow $ADMIN_PORT/tcp
        sudo ufw allow $SMARTUI_PORT/tcp
        sudo ufw --force enable
    fi
    
    log_success "防火墙配置完成"
}

# 启动服务
start_services() {
    log_info "启动PowerAutomation服务..."
    
    # 启动Admin服务
    sudo systemctl start powerautomation-admin
    sleep 5
    
    # 启动SmartUI服务
    sudo systemctl start powerautomation-smartui
    sleep 5
    
    # 重启Nginx
    sudo systemctl restart nginx
    
    log_success "所有服务启动完成"
}

# 验证部署
verify_deployment() {
    log_info "验证部署结果..."
    
    # 检查服务状态
    if sudo systemctl is-active --quiet powerautomation-admin; then
        log_success "Admin服务运行正常 (端口:$ADMIN_PORT)"
    else
        log_error "Admin服务启动失败"
        sudo systemctl status powerautomation-admin
    fi
    
    if sudo systemctl is-active --quiet powerautomation-smartui; then
        log_success "SmartUI MCP服务运行正常 (端口:$SMARTUI_PORT)"
    else
        log_error "SmartUI MCP服务启动失败"
        sudo systemctl status powerautomation-smartui
    fi
    
    # 检查端口监听
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
    sleep 10
    if curl -f http://localhost/health > /dev/null 2>&1; then
        log_success "HTTP健康检查通过"
    else
        log_warning "HTTP健康检查失败，可能需要等待服务完全启动"
    fi
}

# 显示部署信息
show_deployment_info() {
    log_success "PowerAutomation远程部署完成！"
    echo ""
    echo "=========================================="
    echo "部署信息:"
    echo "=========================================="
    echo "服务器: 98.81.255.168"
    echo "安装目录: $INSTALL_DIR"
    echo "Admin后台: http://98.81.255.168/admin (端口:$ADMIN_PORT)"
    echo "SmartUI MCP: http://98.81.255.168 (端口:$SMARTUI_PORT)"
    echo "健康检查: http://98.81.255.168/health"
    echo ""
    echo "服务管理命令:"
    echo "Admin服务: sudo systemctl {start|stop|restart|status} powerautomation-admin"
    echo "SmartUI服务: sudo systemctl {start|stop|restart|status} powerautomation-smartui"
    echo "Nginx服务: sudo systemctl {start|stop|restart|status} nginx"
    echo ""
    echo "日志查看:"
    echo "Admin日志: sudo journalctl -u powerautomation-admin -f"
    echo "SmartUI日志: sudo journalctl -u powerautomation-smartui -f"
    echo "Nginx日志: sudo tail -f /var/log/nginx/access.log"
    echo ""
    echo "配置文件:"
    echo "主配置: $INSTALL_DIR/config/production.yaml"
    echo "端口配置: $INSTALL_DIR/config/ports.yaml"
    echo "Nginx配置: /etc/nginx/conf.d/powerautomation.conf"
    echo "=========================================="
}

# 主函数
main() {
    echo "PowerAutomation 远程部署脚本"
    echo "目标服务器: 98.81.255.168"
    echo "Admin端口: $ADMIN_PORT"
    echo "SmartUI端口: $SMARTUI_PORT"
    echo "============================="
    echo ""
    
    check_system
    install_dependencies
    setup_code
    setup_python_env
    configure_ports
    setup_database
    setup_redis
    create_services
    setup_nginx
    setup_firewall
    start_services
    verify_deployment
    show_deployment_info
}

# 错误处理
trap 'log_error "部署过程中发生错误，请检查日志"; exit 1' ERR

# 运行主函数
main "$@"

