#!/bin/bash
# PowerAutomation 快速部署脚本
# 版本: 1.0.0
# 作者: PowerAutomation Team
# 日期: 2025-06-17

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置变量
REPO_URL="https://github.com/alexchuang650730/aicore0615.git"
INSTALL_DIR="/opt/powerautomation"
SERVICE_USER="powerautomation"
PYTHON_VERSION="3.11"

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

# 检查是否为root用户
check_root() {
    if [[ $EUID -eq 0 ]]; then
        log_error "请不要使用root用户运行此脚本"
        exit 1
    fi
}

# 检查操作系统
check_os() {
    log_info "检查操作系统..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if [ -f /etc/os-release ]; then
            . /etc/os-release
            OS=$NAME
            VER=$VERSION_ID
            log_info "检测到操作系统: $OS $VER"
        else
            log_error "无法检测操作系统版本"
            exit 1
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macOS"
        VER=$(sw_vers -productVersion)
        log_info "检测到操作系统: $OS $VER"
    else
        log_error "不支持的操作系统: $OSTYPE"
        exit 1
    fi
}

# 检查系统要求
check_requirements() {
    log_info "检查系统要求..."
    
    # 检查内存
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        MEMORY_GB=$(free -g | awk '/^Mem:/{print $2}')
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        MEMORY_GB=$(( $(sysctl -n hw.memsize) / 1024 / 1024 / 1024 ))
    fi
    
    if [ $MEMORY_GB -lt 4 ]; then
        log_warning "系统内存少于4GB，可能影响性能"
    else
        log_success "内存检查通过: ${MEMORY_GB}GB"
    fi
    
    # 检查磁盘空间
    DISK_SPACE=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
    if [ $DISK_SPACE -lt 10 ]; then
        log_error "磁盘空间不足，至少需要10GB"
        exit 1
    else
        log_success "磁盘空间检查通过: ${DISK_SPACE}GB可用"
    fi
}

# 安装系统依赖
install_system_dependencies() {
    log_info "安装系统依赖..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v apt-get &> /dev/null; then
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
                postgresql-client \
                redis-tools \
                nginx
        elif command -v yum &> /dev/null; then
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
                postgresql \
                redis \
                nginx
        else
            log_error "不支持的Linux发行版"
            exit 1
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        if ! command -v brew &> /dev/null; then
            log_info "安装Homebrew..."
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        fi
        
        brew update
        brew install \
            git \
            python@3.11 \
            postgresql \
            redis \
            nginx
    fi
    
    log_success "系统依赖安装完成"
}

# 检查Python版本
check_python() {
    log_info "检查Python版本..."
    
    if command -v python3.11 &> /dev/null; then
        PYTHON_CMD="python3.11"
    elif command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
        PYTHON_VER=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
        if [[ "$PYTHON_VER" < "3.11" ]]; then
            log_warning "Python版本 $PYTHON_VER 可能不兼容，建议使用3.11+"
        fi
    else
        log_error "未找到Python 3"
        exit 1
    fi
    
    log_success "Python检查通过: $($PYTHON_CMD --version)"
}

# 克隆代码仓库
clone_repository() {
    log_info "克隆PowerAutomation代码仓库..."
    
    if [ -d "$INSTALL_DIR" ]; then
        log_warning "目录 $INSTALL_DIR 已存在，正在备份..."
        sudo mv "$INSTALL_DIR" "${INSTALL_DIR}.backup.$(date +%Y%m%d_%H%M%S)"
    fi
    
    sudo mkdir -p "$INSTALL_DIR"
    sudo chown $USER:$USER "$INSTALL_DIR"
    
    git clone "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
    
    log_success "代码仓库克隆完成"
}

# 创建Python虚拟环境
create_virtual_environment() {
    log_info "创建Python虚拟环境..."
    
    cd "$INSTALL_DIR"
    $PYTHON_CMD -m venv venv
    source venv/bin/activate
    
    # 升级pip
    pip install --upgrade pip
    
    # 安装依赖
    if [ -f requirements.txt ]; then
        pip install -r requirements.txt
    else
        log_warning "未找到requirements.txt，安装基础依赖..."
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
    fi
    
    log_success "Python虚拟环境创建完成"
}

# 配置数据库
setup_database() {
    log_info "配置数据库..."
    
    # 检查PostgreSQL是否运行
    if ! pgrep -x "postgres" > /dev/null; then
        log_info "启动PostgreSQL服务..."
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            sudo systemctl start postgresql
            sudo systemctl enable postgresql
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            brew services start postgresql
        fi
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
    
    # 检查Redis是否运行
    if ! pgrep -x "redis-server" > /dev/null; then
        log_info "启动Redis服务..."
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            sudo systemctl start redis
            sudo systemctl enable redis
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            brew services start redis
        fi
    fi
    
    # 测试Redis连接
    if redis-cli ping | grep -q "PONG"; then
        log_success "Redis配置完成"
    else
        log_error "Redis连接失败"
        exit 1
    fi
}

# 创建配置文件
create_config() {
    log_info "创建配置文件..."
    
    cd "$INSTALL_DIR"
    
    # 创建主配置文件
    cat > config/production.yaml << EOF
# PowerAutomation 生产环境配置
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

server:
  host: "0.0.0.0"
  port: 8000
  workers: 4

features:
  smartui_mcp: true
  enhanced_workflow: true
  test_framework: true
  monitoring: true
EOF
    
    # 创建环境变量文件
    cat > .env << EOF
POWERAUTOMATION_ENV=production
DATABASE_URL=postgresql://powerautomation:powerautomation@localhost:5432/powerautomation
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=$(openssl rand -hex 32)
EOF
    
    log_success "配置文件创建完成"
}

# 创建系统服务
create_systemd_service() {
    log_info "创建系统服务..."
    
    sudo tee /etc/systemd/system/powerautomation.service > /dev/null << EOF
[Unit]
Description=PowerAutomation Service
After=network.target postgresql.service redis.service
Wants=postgresql.service redis.service

[Service]
Type=simple
User=$USER
Group=$USER
WorkingDirectory=$INSTALL_DIR
Environment=PATH=$INSTALL_DIR/venv/bin
ExecStart=$INSTALL_DIR/venv/bin/python main.py
ExecReload=/bin/kill -HUP \$MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    sudo systemctl daemon-reload
    sudo systemctl enable powerautomation
    
    log_success "系统服务创建完成"
}

# 配置Nginx
setup_nginx() {
    log_info "配置Nginx..."
    
    sudo tee /etc/nginx/sites-available/powerautomation > /dev/null << EOF
server {
    listen 80;
    server_name localhost;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    location /static/ {
        alias $INSTALL_DIR/static/;
        expires 30d;
    }
    
    location /health {
        access_log off;
        proxy_pass http://127.0.0.1:8000/health;
    }
}
EOF
    
    sudo ln -sf /etc/nginx/sites-available/powerautomation /etc/nginx/sites-enabled/
    sudo nginx -t
    sudo systemctl restart nginx
    sudo systemctl enable nginx
    
    log_success "Nginx配置完成"
}

# 运行初始化
run_initialization() {
    log_info "运行系统初始化..."
    
    cd "$INSTALL_DIR"
    source venv/bin/activate
    
    # 运行数据库迁移
    if [ -f manage.py ]; then
        python manage.py migrate
    fi
    
    # 创建测试数据
    if [ -f scripts/seed_data.py ]; then
        python scripts/seed_data.py
    fi
    
    log_success "系统初始化完成"
}

# 启动服务
start_services() {
    log_info "启动PowerAutomation服务..."
    
    sudo systemctl start powerautomation
    
    # 等待服务启动
    sleep 10
    
    # 检查服务状态
    if sudo systemctl is-active --quiet powerautomation; then
        log_success "PowerAutomation服务启动成功"
    else
        log_error "PowerAutomation服务启动失败"
        sudo systemctl status powerautomation
        exit 1
    fi
}

# 运行健康检查
health_check() {
    log_info "运行健康检查..."
    
    # 检查HTTP响应
    if curl -f http://localhost/health > /dev/null 2>&1; then
        log_success "HTTP健康检查通过"
    else
        log_error "HTTP健康检查失败"
        exit 1
    fi
    
    # 检查数据库连接
    cd "$INSTALL_DIR"
    source venv/bin/activate
    if python -c "import psycopg2; psycopg2.connect('postgresql://powerautomation:powerautomation@localhost:5432/powerautomation')" 2>/dev/null; then
        log_success "数据库连接检查通过"
    else
        log_error "数据库连接检查失败"
        exit 1
    fi
    
    # 检查Redis连接
    if redis-cli ping | grep -q "PONG"; then
        log_success "Redis连接检查通过"
    else
        log_error "Redis连接检查失败"
        exit 1
    fi
}

# 显示部署信息
show_deployment_info() {
    log_success "PowerAutomation部署完成！"
    echo ""
    echo "=========================================="
    echo "部署信息:"
    echo "=========================================="
    echo "安装目录: $INSTALL_DIR"
    echo "访问地址: http://localhost"
    echo "健康检查: http://localhost/health"
    echo "配置文件: $INSTALL_DIR/config/production.yaml"
    echo "日志文件: /var/log/powerautomation/app.log"
    echo ""
    echo "服务管理命令:"
    echo "启动服务: sudo systemctl start powerautomation"
    echo "停止服务: sudo systemctl stop powerautomation"
    echo "重启服务: sudo systemctl restart powerautomation"
    echo "查看状态: sudo systemctl status powerautomation"
    echo "查看日志: sudo journalctl -u powerautomation -f"
    echo ""
    echo "组件测试:"
    echo "SmartUI MCP: cd $INSTALL_DIR/mcp/adapter/smartui_mcp && python cli.py status"
    echo "测试框架: cd $INSTALL_DIR/test && python cli.py status"
    echo ""
    echo "=========================================="
}

# 主函数
main() {
    echo "PowerAutomation 快速部署脚本"
    echo "============================="
    echo ""
    
    check_root
    check_os
    check_requirements
    install_system_dependencies
    check_python
    clone_repository
    create_virtual_environment
    setup_database
    setup_redis
    create_config
    create_systemd_service
    setup_nginx
    run_initialization
    start_services
    health_check
    show_deployment_info
}

# 错误处理
trap 'log_error "部署过程中发生错误，请检查日志"; exit 1' ERR

# 运行主函数
main "$@"

