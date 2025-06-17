FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件并安装Python包
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建必要的目录
RUN mkdir -p logs data

# 设置权限
RUN chmod +x run_tests.py

# 创建非root用户
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8096/api/health || exit 1

# 暴露端口
EXPOSE 8096

# 设置环境变量
ENV PYTHONPATH=/app
ENV FLASK_ENV=production

# 启动命令
CMD ["python", "src/human_loop_server.py", "--config", "config/human_loop_mcp_config.yaml"]

