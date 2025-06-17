#!/bin/bash

# Human-in-the-Loop MCP 启动脚本
# 用于快速启动和管理服务

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="/home/ubuntu/aicore0615/mcp/adapter/human_loop_mcp"
cd "$PROJECT_ROOT"

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

# 检查依赖
check_dependencies() {
    log_info "检查依赖..."
    
    # 检查Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装"
        exit 1
    fi
    
    # 检查pip
    if ! command -v pip3 &> /dev/null; then
        log_error "pip3 未安装"
        exit 1
    fi
    
    log_success "依赖检查完成"
}

# 安装Python依赖
install_dependencies() {
    log_info "安装Python依赖..."
    
    if [ -f "requirements.txt" ]; then
        pip3 install -r requirements.txt
        log_success "Python依赖安装完成"
    else
        log_warning "requirements.txt 文件不存在"
    fi
}

# 创建必要目录
create_directories() {
    log_info "创建必要目录..."
    
    mkdir -p logs
    mkdir -p data
    mkdir -p config
    
    log_success "目录创建完成"
}

# 检查配置文件
check_config() {
    log_info "检查配置文件..."
    
    if [ ! -f "config/human_loop_mcp_config.yaml" ]; then
        log_warning "配置文件不存在，创建默认配置..."
        
        cat > config/human_loop_mcp_config.yaml << EOF
service:
  name: "human_loop_mcp"
  version: "1.0.0"
  description: "Human-in-the-Loop Model Control Protocol"

server:
  host: "0.0.0.0"
  port: 8096
  debug: false

database:
  type: "sqlite"
  path: "data/human_loop.db"

redis:
  host: "localhost"
  port: 6379
  db: 5

session:
  default_timeout: 300
  max_timeout: 3600
  cleanup_interval: 60

logging:
  level: "INFO"
  file: "logs/human_loop_mcp.log"
  max_size: "10MB"
  backup_count: 5

security:
  enable_auth: false
  session_secret: "human-loop-secret-key-2025"
  cors_origins: ["*"]

integration:
  mcp_coordinator_url: "http://localhost:8090"
  workflow_callback_timeout: 30
EOF
        
        log_success "默认配置文件已创建"
    else
        log_success "配置文件检查完成"
    fi
}

# 运行测试
run_tests() {
    log_info "运行测试..."
    
    if [ -f "run_tests.py" ]; then
        python3 run_tests.py --unit
        log_success "测试完成"
    else
        log_warning "测试文件不存在"
    fi
}

# 启动服务
start_service() {
    log_info "启动 Human-in-the-Loop MCP 服务..."
    
    # 检查端口是否被占用
    if netstat -tlnp 2>/dev/null | grep -q ":8096 "; then
        log_error "端口 8096 已被占用"
        exit 1
    fi
    
    # 设置环境变量
    export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"
    
    # 启动服务
    python3 src/human_loop_server.py --config config/human_loop_mcp_config.yaml
}

# 停止服务
stop_service() {
    log_info "停止 Human-in-the-Loop MCP 服务..."
    
    # 查找并杀死进程
    PID=$(ps aux | grep "human_loop_server.py" | grep -v grep | awk '{print $2}')
    
    if [ -n "$PID" ]; then
        kill -TERM "$PID"
        sleep 2
        
        # 如果进程仍在运行，强制杀死
        if ps -p "$PID" > /dev/null 2>&1; then
            kill -KILL "$PID"
            log_warning "强制停止服务"
        else
            log_success "服务已停止"
        fi
    else
        log_warning "服务未运行"
    fi
}

# 重启服务
restart_service() {
    log_info "重启 Human-in-the-Loop MCP 服务..."
    stop_service
    sleep 2
    start_service
}

# 查看服务状态
status_service() {
    log_info "检查服务状态..."
    
    # 检查进程
    PID=$(ps aux | grep "human_loop_server.py" | grep -v grep | awk '{print $2}')
    
    if [ -n "$PID" ]; then
        log_success "服务正在运行 (PID: $PID)"
        
        # 检查API健康状态
        if command -v curl &> /dev/null; then
            if curl -s http://localhost:8096/api/health > /dev/null; then
                log_success "API 健康检查通过"
            else
                log_warning "API 健康检查失败"
            fi
        fi
    else
        log_warning "服务未运行"
    fi
}

# 查看日志
view_logs() {
    log_info "查看服务日志..."
    
    if [ -f "logs/human_loop_mcp.log" ]; then
        tail -f logs/human_loop_mcp.log
    else
        log_warning "日志文件不存在"
    fi
}

# 清理数据
clean_data() {
    log_info "清理数据..."
    
    read -p "确定要清理所有数据吗？这将删除数据库和日志文件 (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -f data/human_loop.db
        rm -f logs/*.log
        log_success "数据清理完成"
    else
        log_info "取消清理操作"
    fi
}

# Docker 相关操作
docker_build() {
    log_info "构建 Docker 镜像..."
    docker build -t human-loop-mcp:latest .
    log_success "Docker 镜像构建完成"
}

docker_up() {
    log_info "启动 Docker 容器..."
    docker-compose up -d
    log_success "Docker 容器启动完成"
}

docker_down() {
    log_info "停止 Docker 容器..."
    docker-compose down
    log_success "Docker 容器停止完成"
}

docker_logs() {
    log_info "查看 Docker 容器日志..."
    docker-compose logs -f human-loop-mcp
}

# 显示帮助信息
show_help() {
    echo "Human-in-the-Loop MCP 管理脚本"
    echo ""
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  setup           初始化环境（安装依赖、创建目录、检查配置）"
    echo "  start           启动服务"
    echo "  stop            停止服务"
    echo "  restart         重启服务"
    echo "  status          查看服务状态"
    echo "  logs            查看服务日志"
    echo "  test            运行测试"
    echo "  clean           清理数据"
    echo ""
    echo "Docker 命令:"
    echo "  docker-build    构建 Docker 镜像"
    echo "  docker-up       启动 Docker 容器"
    echo "  docker-down     停止 Docker 容器"
    echo "  docker-logs     查看 Docker 容器日志"
    echo ""
    echo "  help            显示此帮助信息"
}

# 主函数
main() {
    case "${1:-help}" in
        setup)
            check_dependencies
            install_dependencies
            create_directories
            check_config
            log_success "环境初始化完成"
            ;;
        start)
            start_service
            ;;
        stop)
            stop_service
            ;;
        restart)
            restart_service
            ;;
        status)
            status_service
            ;;
        logs)
            view_logs
            ;;
        test)
            run_tests
            ;;
        clean)
            clean_data
            ;;
        docker-build)
            docker_build
            ;;
        docker-up)
            docker_up
            ;;
        docker-down)
            docker_down
            ;;
        docker-logs)
            docker_logs
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "未知命令: $1"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"

