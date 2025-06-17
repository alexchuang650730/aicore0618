#!/bin/bash
# PowerAutomation Docker 快速部署脚本
# 版本: 1.0.0

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

# 检查Docker
check_docker() {
    log_info "检查Docker环境..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker未安装，请先安装Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose未安装，请先安装Docker Compose"
        exit 1
    fi
    
    log_success "Docker环境检查通过"
}

# 创建Docker Compose文件
create_docker_compose() {
    log_info "创建Docker Compose配置..."
    
    cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  powerautomation:
    image: powerautomation/powerautomation:latest
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://powerautomation:powerautomation@db:5432/powerautomation
      - REDIS_URL=redis://redis:6379/0
      - SECRET_KEY=your-secret-key-here
    depends_on:
      - db
      - redis
    volumes:
      - ./logs:/app/logs
      - ./config:/app/config
    restart: unless-stopped

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: powerautomation
      POSTGRES_USER: powerautomation
      POSTGRES_PASSWORD: powerautomation
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - powerautomation
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
EOF

    log_success "Docker Compose配置创建完成"
}

# 创建Dockerfile
create_dockerfile() {
    log_info "创建Dockerfile..."
    
    cat > Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建非root用户
RUN useradd -m -u 1000 powerautomation && \
    chown -R powerautomation:powerautomation /app

USER powerautomation

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 启动命令
CMD ["python", "main.py"]
EOF

    log_success "Dockerfile创建完成"
}

# 创建Nginx配置
create_nginx_config() {
    log_info "创建Nginx配置..."
    
    cat > nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream powerautomation {
        server powerautomation:8000;
    }

    server {
        listen 80;
        server_name localhost;

        location / {
            proxy_pass http://powerautomation;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        location /health {
            access_log off;
            proxy_pass http://powerautomation/health;
        }
    }
}
EOF

    log_success "Nginx配置创建完成"
}

# 创建requirements.txt
create_requirements() {
    log_info "创建requirements.txt..."
    
    cat > requirements.txt << 'EOF'
asyncio
pyyaml
pathlib
fastapi==0.104.1
uvicorn[standard]==0.24.0
flask==3.0.0
requests==2.31.0
pandas==2.1.4
numpy==1.24.3
matplotlib==3.8.2
seaborn==0.13.0
beautifulsoup4==4.12.2
markdown==3.5.1
reportlab==4.0.7
psycopg2-binary==2.9.9
redis==5.0.1
python-multipart==0.0.6
jinja2==3.1.2
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0
EOF

    log_success "requirements.txt创建完成"
}

# 部署应用
deploy_application() {
    log_info "部署PowerAutomation应用..."
    
    # 构建并启动服务
    docker-compose up -d --build
    
    log_info "等待服务启动..."
    sleep 30
    
    # 检查服务状态
    docker-compose ps
    
    log_success "应用部署完成"
}

# 健康检查
health_check() {
    log_info "运行健康检查..."
    
    # 检查HTTP响应
    if curl -f http://localhost/health > /dev/null 2>&1; then
        log_success "HTTP健康检查通过"
    else
        log_error "HTTP健康检查失败"
        docker-compose logs powerautomation
        exit 1
    fi
}

# 显示部署信息
show_info() {
    log_success "PowerAutomation Docker部署完成！"
    echo ""
    echo "=========================================="
    echo "部署信息:"
    echo "=========================================="
    echo "访问地址: http://localhost"
    echo "健康检查: http://localhost/health"
    echo "数据库: localhost:5432"
    echo "Redis: localhost:6379"
    echo ""
    echo "Docker管理命令:"
    echo "查看状态: docker-compose ps"
    echo "查看日志: docker-compose logs -f"
    echo "停止服务: docker-compose down"
    echo "重启服务: docker-compose restart"
    echo "更新应用: docker-compose up -d --build"
    echo ""
    echo "=========================================="
}

# 主函数
main() {
    echo "PowerAutomation Docker 快速部署"
    echo "==============================="
    echo ""
    
    check_docker
    create_docker_compose
    create_dockerfile
    create_nginx_config
    create_requirements
    deploy_application
    health_check
    show_info
}

# 运行主函数
main "$@"

