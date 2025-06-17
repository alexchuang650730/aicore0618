# Human-in-the-Loop MCP 组件

## 概述

Human-in-the-Loop MCP (Model Control Protocol) 是 PowerAutomation 项目中的核心组件，专门设计用于在自动化工作流中引入人工决策点。该组件提供了一个完整的人机交互解决方案，允许工作流在关键决策点暂停并等待人工输入，确保自动化系统在复杂场景下的可控性和可靠性。

本组件采用现代化的 Web 技术栈，提供直观的用户界面和强大的后端服务，支持多种交互类型，包括确认对话框、选择列表、文本输入和文件上传等。通过 RESTful API 和 WebSocket 实时通信，确保了与其他系统组件的无缝集成。

## 核心特性

### 多样化交互类型
- **确认对话框**: 用于需要用户确认的关键操作
- **选择列表**: 支持单选和多选的选项列表
- **文本输入**: 灵活的表单输入，支持多种字段类型
- **文件上传**: 安全的文件上传功能，支持多种文件格式

### 实时通信
- WebSocket 连接确保实时状态更新
- 自动重连机制保证连接稳定性
- 推送通知及时告知用户新的交互请求

### 会话管理
- 智能会话生命周期管理
- 自动超时处理机制
- 持久化存储支持数据恢复

### 高可用性设计
- Redis 缓存提升性能
- SQLite 数据库确保数据持久性
- 多线程架构支持并发处理

## 技术架构

### 后端架构
后端采用 Python Flask 框架构建，提供 RESTful API 接口和 WebSocket 实时通信能力。核心组件包括：

- **会话管理器 (SessionManager)**: 负责交互会话的创建、更新、完成和清理
- **数据模型 (Models)**: 定义交互数据结构和会话状态
- **API 服务器 (HumanLoopMCPServer)**: 提供 HTTP API 和 WebSocket 服务

### 前端架构
前端采用现代化的 Web 技术，包括：

- **HTML5**: 语义化标记和响应式布局
- **CSS3**: 现代化样式设计和动画效果
- **JavaScript ES6+**: 模块化代码和异步处理
- **Socket.IO**: 实时双向通信

### 数据存储
- **SQLite**: 主要数据存储，支持事务和并发访问
- **Redis**: 缓存和会话状态管理（可选）
- **文件系统**: 日志和临时文件存储

## 目录结构

```
mcp/adapter/human_loop_mcp/
├── src/                          # 源代码目录
│   ├── models.py                 # 数据模型定义
│   ├── session_manager.py        # 会话管理器
│   └── human_loop_server.py      # API服务器
├── config/                       # 配置文件目录
│   └── human_loop_mcp_config.yaml
├── frontend/                     # 前端资源目录
│   ├── index.html               # 主页面
│   ├── css/
│   │   └── main.css             # 样式文件
│   └── js/
│       └── main.js              # 交互逻辑
├── unit_tests/                   # 单元测试
│   └── test_models_and_session.py
├── integration_tests/            # 集成测试
│   └── test_api_integration.py
├── logs/                         # 日志目录
├── data/                         # 数据目录
├── run_tests.py                  # 测试运行器
└── README.md                     # 本文档
```

## 快速开始

### 环境要求

- Python 3.8+
- pip 包管理器
- Redis (可选，用于缓存)

### 安装依赖

```bash
cd /home/ubuntu/aicore0615/mcp/adapter/human_loop_mcp
pip install -r requirements.txt
```

### 配置文件

编辑 `config/human_loop_mcp_config.yaml` 文件，根据您的环境调整配置：

```yaml
server:
  host: "0.0.0.0"
  port: 8096
  debug: false

database:
  type: "sqlite"
  path: "data/human_loop.db"

redis:
  host: "localhost"  # 设置为 null 禁用 Redis
  port: 6379
  db: 5
```

### 启动服务

```bash
python src/human_loop_server.py --config config/human_loop_mcp_config.yaml
```

服务启动后，可以通过以下地址访问：
- Web 界面: http://localhost:8096
- API 文档: http://localhost:8096/api/health

### 运行测试

```bash
# 运行所有测试
python run_tests.py

# 只运行单元测试
python run_tests.py --unit

# 只运行集成测试
python run_tests.py --integration
```

## API 接口文档

### 健康检查

**GET** `/api/health`

检查服务健康状态和获取基本信息。

**响应示例:**
```json
{
  "status": "healthy",
  "timestamp": "2025-06-17T10:30:00Z",
  "version": "1.0.0",
  "service": "human_loop_mcp",
  "statistics": {
    "active_sessions": 3,
    "total_sessions": 156,
    "completed_sessions": 142
  }
}
```

### 创建交互会话

**POST** `/api/sessions`

创建新的人机交互会话。

**请求体:**
```json
{
  "interaction_data": {
    "interaction_type": "confirmation",
    "title": "确认部署",
    "message": "确定要部署到生产环境吗？",
    "options": [
      {"value": "confirm", "label": "确认"},
      {"value": "cancel", "label": "取消"}
    ],
    "timeout": 300
  },
  "workflow_id": "deployment-workflow-123",
  "callback_url": "http://workflow.example.com/callback"
}
```

**响应示例:**
```json
{
  "success": true,
  "session_id": "session-uuid-12345",
  "session": {
    "session_id": "session-uuid-12345",
    "workflow_id": "deployment-workflow-123",
    "status": "pending",
    "created_at": "2025-06-17T10:30:00Z",
    "expires_at": "2025-06-17T10:35:00Z",
    "interaction_data": {
      "interaction_type": "confirmation",
      "title": "确认部署",
      "message": "确定要部署到生产环境吗？"
    }
  }
}
```

### 获取会话信息

**GET** `/api/sessions/{session_id}`

获取指定会话的详细信息。

**响应示例:**
```json
{
  "success": true,
  "session": {
    "session_id": "session-uuid-12345",
    "workflow_id": "deployment-workflow-123",
    "status": "pending",
    "created_at": "2025-06-17T10:30:00Z",
    "updated_at": "2025-06-17T10:30:00Z",
    "expires_at": "2025-06-17T10:35:00Z",
    "interaction_data": {
      "interaction_type": "confirmation",
      "title": "确认部署",
      "message": "确定要部署到生产环境吗？",
      "options": [
        {"value": "confirm", "label": "确认"},
        {"value": "cancel", "label": "取消"}
      ]
    }
  }
}
```

### 提交用户响应

**POST** `/api/sessions/{session_id}/respond`

提交用户对交互会话的响应。

**请求体:**
```json
{
  "response": {
    "choice": "confirm"
  },
  "user_id": "user-123"
}
```

**响应示例:**
```json
{
  "success": true,
  "message": "响应已提交"
}
```

### 取消会话

**POST** `/api/sessions/{session_id}/cancel`

取消指定的交互会话。

**请求体:**
```json
{
  "reason": "用户取消操作"
}
```

**响应示例:**
```json
{
  "success": true,
  "message": "会话已取消"
}
```

### 获取会话列表

**GET** `/api/sessions`

获取活跃会话列表，支持按工作流ID过滤。

**查询参数:**
- `workflow_id` (可选): 过滤指定工作流的会话

**响应示例:**
```json
{
  "success": true,
  "sessions": [
    {
      "session_id": "session-uuid-12345",
      "workflow_id": "deployment-workflow-123",
      "status": "pending",
      "created_at": "2025-06-17T10:30:00Z",
      "interaction_data": {
        "title": "确认部署",
        "interaction_type": "confirmation"
      }
    }
  ]
}
```

### 获取统计信息

**GET** `/api/statistics`

获取系统统计信息。

**响应示例:**
```json
{
  "success": true,
  "statistics": {
    "active_sessions": 3,
    "total_sessions": 156,
    "completed_sessions": 142,
    "timeout_sessions": 8,
    "cancelled_sessions": 6
  }
}
```

### 获取交互模板

**GET** `/api/templates`

获取预定义的交互模板。

**响应示例:**
```json
{
  "success": true,
  "templates": {
    "confirmation": {
      "name": "确认对话框",
      "description": "用于需要用户确认的场景",
      "example": {
        "interaction_type": "confirmation",
        "title": "确认操作",
        "message": "是否继续执行？",
        "options": [
          {"value": "confirm", "label": "确认"},
          {"value": "cancel", "label": "取消"}
        ]
      }
    }
  }
}
```

## 交互类型详解

### 确认对话框 (Confirmation)

确认对话框是最简单的交互类型，用于需要用户做出是/否决策的场景。

**使用场景:**
- 部署确认
- 删除操作确认
- 重要配置变更确认

**配置示例:**
```json
{
  "interaction_type": "confirmation",
  "title": "删除确认",
  "message": "确定要删除这个文件吗？此操作不可撤销。",
  "options": [
    {"value": "confirm", "label": "确认删除"},
    {"value": "cancel", "label": "取消"}
  ],
  "default_value": "cancel",
  "timeout": 300
}
```

### 选择列表 (Selection)

选择列表允许用户从预定义的选项中选择一个或多个值。

**使用场景:**
- 环境选择（开发/测试/生产）
- 配置选项选择
- 多项功能启用/禁用

**单选配置示例:**
```json
{
  "interaction_type": "selection",
  "title": "选择部署环境",
  "message": "请选择要部署的目标环境",
  "options": [
    {"value": "dev", "label": "开发环境"},
    {"value": "staging", "label": "测试环境"},
    {"value": "prod", "label": "生产环境"}
  ],
  "multiple": false,
  "timeout": 600
}
```

**多选配置示例:**
```json
{
  "interaction_type": "selection",
  "title": "选择功能模块",
  "message": "请选择要启用的功能模块",
  "options": [
    {"value": "auth", "label": "用户认证"},
    {"value": "logging", "label": "日志记录"},
    {"value": "monitoring", "label": "监控告警"},
    {"value": "backup", "label": "数据备份"}
  ],
  "multiple": true,
  "timeout": 900
}
```

### 文本输入 (Text Input)

文本输入类型支持复杂的表单输入，可以包含多个不同类型的字段。

**使用场景:**
- 配置参数输入
- 用户信息收集
- 自定义设置

**配置示例:**
```json
{
  "interaction_type": "text_input",
  "title": "服务器配置",
  "message": "请填写服务器配置信息",
  "fields": [
    {
      "name": "server_name",
      "label": "服务器名称",
      "field_type": "text",
      "required": true,
      "validation": "^[a-zA-Z0-9-]+$"
    },
    {
      "name": "port",
      "label": "端口号",
      "field_type": "number",
      "required": true,
      "min_value": 1,
      "max_value": 65535,
      "default": 8080
    },
    {
      "name": "admin_email",
      "label": "管理员邮箱",
      "field_type": "email",
      "required": true
    },
    {
      "name": "description",
      "label": "描述信息",
      "field_type": "textarea",
      "required": false
    }
  ],
  "timeout": 1200
}
```

### 文件上传 (File Upload)

文件上传类型允许用户上传配置文件、证书或其他必要的文件。

**使用场景:**
- 配置文件上传
- 证书文件上传
- 数据文件导入

**配置示例:**
```json
{
  "interaction_type": "file_upload",
  "title": "上传配置文件",
  "message": "请上传应用配置文件",
  "accept_types": [".json", ".yaml", ".yml", ".xml"],
  "max_file_size": "10MB",
  "multiple": false,
  "timeout": 1800
}
```

## 集成指南

### 与工作流系统集成

Human-in-the-Loop MCP 设计为与现有工作流系统无缝集成。以下是典型的集成模式：

#### 1. 同步集成模式

在同步模式下，工作流直接调用 Human-in-the-Loop MCP API 并等待响应：

```python
import requests
import time

def request_human_approval(workflow_id, decision_data):
    """请求人工审批"""
    
    # 创建交互会话
    session_data = {
        "interaction_data": {
            "interaction_type": "confirmation",
            "title": "审批请求",
            "message": f"工作流 {workflow_id} 需要您的审批",
            "timeout": 600
        },
        "workflow_id": workflow_id,
        "callback_url": None  # 同步模式不需要回调
    }
    
    response = requests.post(
        "http://localhost:8096/api/sessions",
        json=session_data
    )
    
    if response.status_code != 200:
        raise Exception("创建会话失败")
    
    session_id = response.json()["session_id"]
    
    # 轮询等待用户响应
    while True:
        response = requests.get(
            f"http://localhost:8096/api/sessions/{session_id}"
        )
        
        if response.status_code == 200:
            session = response.json()["session"]
            
            if session["status"] == "completed":
                return session["response"]["response_data"]
            elif session["status"] in ["timeout", "cancelled", "error"]:
                raise Exception(f"会话失败: {session['status']}")
        
        time.sleep(5)  # 5秒后重试
```

#### 2. 异步集成模式

在异步模式下，工作流创建会话后继续执行其他任务，通过回调接收结果：

```python
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

def request_human_approval_async(workflow_id, decision_data):
    """异步请求人工审批"""
    
    session_data = {
        "interaction_data": {
            "interaction_type": "selection",
            "title": "环境选择",
            "message": "请选择部署环境",
            "options": [
                {"value": "staging", "label": "测试环境"},
                {"value": "prod", "label": "生产环境"}
            ]
        },
        "workflow_id": workflow_id,
        "callback_url": "http://workflow.example.com/human_loop_callback"
    }
    
    response = requests.post(
        "http://localhost:8096/api/sessions",
        json=session_data
    )
    
    if response.status_code == 200:
        session_id = response.json()["session_id"]
        print(f"会话已创建: {session_id}")
        return session_id
    else:
        raise Exception("创建会话失败")

@app.route('/human_loop_callback', methods=['POST'])
def human_loop_callback():
    """处理 Human-in-the-Loop 回调"""
    
    data = request.get_json()
    session_id = data["session_id"]
    workflow_id = data["workflow_id"]
    status = data["status"]
    
    if status == "completed":
        response_data = data["response"]["response_data"]
        print(f"工作流 {workflow_id} 收到用户响应: {response_data}")
        
        # 继续执行工作流
        continue_workflow(workflow_id, response_data)
    else:
        print(f"工作流 {workflow_id} 人工交互失败: {status}")
        handle_workflow_failure(workflow_id, status)
    
    return jsonify({"success": True})

def continue_workflow(workflow_id, user_response):
    """根据用户响应继续执行工作流"""
    # 实现工作流继续逻辑
    pass

def handle_workflow_failure(workflow_id, reason):
    """处理工作流失败"""
    # 实现失败处理逻辑
    pass
```

### 与现有 MCP 组件集成

Human-in-the-Loop MCP 可以与项目中的其他 MCP 组件协同工作：

#### 与配置审查工作流集成

```python
# 在 configurable_review_workflow.py 中的集成示例

class ConfigurableReviewWorkflow:
    def __init__(self):
        self.human_loop_mcp_url = "http://localhost:8096"
    
    async def _execute_human_loop_if_needed(self, context):
        """执行人工循环决策"""
        
        if not self._determine_human_loop_requirements(context):
            return {"decision": "auto_approved", "reason": "自动审批"}
        
        # 创建人工交互会话
        session_data = {
            "interaction_data": {
                "interaction_type": "confirmation",
                "title": "代码审查确认",
                "message": f"请审查工作流 {context.get('workflow_id')} 的变更",
                "timeout": 1800  # 30分钟
            },
            "workflow_id": context.get("workflow_id"),
            "callback_url": f"{self.callback_base_url}/review_callback"
        }
        
        try:
            response = requests.post(
                f"{self.human_loop_mcp_url}/api/sessions",
                json=session_data,
                timeout=10
            )
            
            if response.status_code == 200:
                session_id = response.json()["session_id"]
                return {"decision": "pending_human", "session_id": session_id}
            else:
                return {"decision": "error", "reason": "无法创建人工交互会话"}
                
        except Exception as e:
            return {"decision": "error", "reason": f"人工交互服务异常: {str(e)}"}
```

## 部署指南

### 开发环境部署

开发环境部署适用于本地开发和测试：

```bash
# 1. 克隆项目
cd /home/ubuntu/aicore0615/mcp/adapter/human_loop_mcp

# 2. 安装依赖
pip install flask flask-cors flask-socketio redis pyyaml requests

# 3. 创建必要目录
mkdir -p logs data

# 4. 启动服务
python src/human_loop_server.py
```

### 生产环境部署

生产环境部署需要考虑高可用性、安全性和性能：

#### 使用 Docker 部署

创建 `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建必要目录
RUN mkdir -p logs data

# 暴露端口
EXPOSE 8096

# 启动命令
CMD ["python", "src/human_loop_server.py", "--config", "config/human_loop_mcp_config.yaml"]
```

创建 `docker-compose.yml`:

```yaml
version: '3.8'

services:
  human-loop-mcp:
    build: .
    ports:
      - "8096:8096"
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./config:/app/config
    environment:
      - PYTHONPATH=/app
    depends_on:
      - redis
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
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
      - human-loop-mcp
    restart: unless-stopped

volumes:
  redis_data:
```

#### 使用 systemd 部署

创建 systemd 服务文件 `/etc/systemd/system/human-loop-mcp.service`:

```ini
[Unit]
Description=Human-in-the-Loop MCP Service
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/aicore0615/mcp/adapter/human_loop_mcp
Environment=PYTHONPATH=/home/ubuntu/aicore0615
ExecStart=/usr/bin/python3 src/human_loop_server.py --config config/human_loop_mcp_config.yaml
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable human-loop-mcp
sudo systemctl start human-loop-mcp
sudo systemctl status human-loop-mcp
```

### 负载均衡配置

对于高并发场景，可以使用 Nginx 进行负载均衡：

```nginx
upstream human_loop_mcp {
    server 127.0.0.1:8096;
    server 127.0.0.1:8097;
    server 127.0.0.1:8098;
}

server {
    listen 80;
    server_name human-loop.example.com;

    location / {
        proxy_pass http://human_loop_mcp;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /socket.io/ {
        proxy_pass http://human_loop_mcp;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 监控和运维

### 日志管理

Human-in-the-Loop MCP 提供详细的日志记录，支持多种日志级别：

```yaml
# 配置文件中的日志设置
logging:
  level: "INFO"
  file: "logs/human_loop_mcp.log"
  max_size: "10MB"
  backup_count: 5
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

日志文件包含以下信息：
- 会话创建和状态变更
- API 请求和响应
- 错误和异常信息
- 性能指标

### 健康检查

系统提供多层次的健康检查：

```bash
# 基本健康检查
curl http://localhost:8096/api/health

# 详细统计信息
curl http://localhost:8096/api/statistics
```

### 性能监控

可以通过以下指标监控系统性能：

- **活跃会话数**: 当前正在处理的会话数量
- **响应时间**: API 请求的平均响应时间
- **成功率**: 会话成功完成的比例
- **超时率**: 会话超时的比例

### 数据备份

定期备份 SQLite 数据库：

```bash
#!/bin/bash
# backup_script.sh

BACKUP_DIR="/backup/human_loop_mcp"
DB_PATH="/home/ubuntu/aicore0615/mcp/adapter/human_loop_mcp/data/human_loop.db"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

mkdir -p $BACKUP_DIR
cp $DB_PATH "$BACKUP_DIR/human_loop_${TIMESTAMP}.db"

# 保留最近30天的备份
find $BACKUP_DIR -name "human_loop_*.db" -mtime +30 -delete
```

## 故障排除

### 常见问题

#### 1. 服务无法启动

**症状**: 运行 `python src/human_loop_server.py` 时出现错误

**可能原因**:
- 端口被占用
- 配置文件格式错误
- 依赖包未安装

**解决方案**:
```bash
# 检查端口占用
netstat -tlnp | grep 8096

# 验证配置文件
python -c "import yaml; yaml.safe_load(open('config/human_loop_mcp_config.yaml'))"

# 安装依赖
pip install -r requirements.txt
```

#### 2. WebSocket 连接失败

**症状**: 前端无法建立 WebSocket 连接

**可能原因**:
- 防火墙阻止连接
- 代理服务器配置问题
- CORS 设置错误

**解决方案**:
```yaml
# 检查 CORS 配置
security:
  cors_origins: ["*"]  # 开发环境可以使用 *，生产环境应指定具体域名
```

#### 3. 会话超时过快

**症状**: 会话在预期时间之前就超时了

**可能原因**:
- 系统时间不同步
- 清理线程配置错误
- 数据库连接问题

**解决方案**:
```bash
# 同步系统时间
sudo ntpdate -s time.nist.gov

# 检查清理线程配置
session:
  cleanup_interval: 60  # 增加清理间隔
```

#### 4. 数据库锁定错误

**症状**: 出现 "database is locked" 错误

**可能原因**:
- 多个进程同时访问数据库
- 数据库文件权限问题
- 磁盘空间不足

**解决方案**:
```bash
# 检查数据库文件权限
ls -la data/human_loop.db

# 检查磁盘空间
df -h

# 重启服务
sudo systemctl restart human-loop-mcp
```

### 调试模式

启用调试模式获取更详细的错误信息：

```yaml
# 配置文件
server:
  debug: true

logging:
  level: "DEBUG"
```

```bash
# 命令行启动调试模式
python src/human_loop_server.py --config config/human_loop_mcp_config.yaml --debug
```

## 安全考虑

### 认证和授权

虽然当前版本主要用于内部系统，但在生产环境中应考虑添加认证机制：

```yaml
# 配置文件中启用认证
security:
  enable_auth: true
  auth_method: "jwt"  # 或 "basic", "oauth"
  jwt_secret: "your-secret-key"
  token_expiry: 3600
```

### 数据加密

敏感数据应进行加密存储：

```python
# 在 models.py 中添加加密功能
import cryptography.fernet

class EncryptedField:
    def __init__(self, key):
        self.cipher = Fernet(key)
    
    def encrypt(self, data):
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data):
        return self.cipher.decrypt(encrypted_data.encode()).decode()
```

### 网络安全

- 使用 HTTPS 加密传输
- 配置防火墙规则
- 限制 API 访问频率
- 验证输入数据

### 审计日志

记录所有重要操作的审计日志：

```python
def log_audit_event(user_id, action, resource, details):
    """记录审计事件"""
    audit_log = {
        "timestamp": datetime.now().isoformat(),
        "user_id": user_id,
        "action": action,
        "resource": resource,
        "details": details,
        "ip_address": request.remote_addr
    }
    
    logger.info(f"AUDIT: {json.dumps(audit_log)}")
```

## 性能优化

### 数据库优化

- 添加适当的索引
- 定期清理过期数据
- 使用连接池

```sql
-- 添加索引优化查询性能
CREATE INDEX idx_sessions_workflow ON sessions(workflow_id);
CREATE INDEX idx_sessions_status ON sessions(status);
CREATE INDEX idx_sessions_expires ON sessions(expires_at);
```

### 缓存策略

使用 Redis 缓存热点数据：

```python
def get_session_with_cache(session_id):
    """带缓存的会话获取"""
    
    # 先从缓存获取
    if redis_client:
        cached_data = redis_client.get(f"session:{session_id}")
        if cached_data:
            return InteractionSession.from_dict(json.loads(cached_data))
    
    # 缓存未命中，从数据库获取
    session = load_session_from_db(session_id)
    
    # 更新缓存
    if session and redis_client:
        redis_client.setex(
            f"session:{session_id}",
            300,  # 5分钟过期
            json.dumps(session.to_dict())
        )
    
    return session
```

### 并发处理

使用线程池处理并发请求：

```python
from concurrent.futures import ThreadPoolExecutor

class HumanLoopMCPServer:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=10)
    
    def handle_async_callback(self, session):
        """异步处理回调"""
        self.executor.submit(self.send_callback, session)
```

## 扩展开发

### 自定义交互类型

添加新的交互类型：

```python
# 在 models.py 中添加新类型
class InteractionType(Enum):
    CONFIRMATION = "confirmation"
    SELECTION = "selection"
    TEXT_INPUT = "text_input"
    FILE_UPLOAD = "file_upload"
    CUSTOM = "custom"
    # 新增类型
    SIGNATURE = "signature"  # 电子签名
    APPROVAL_CHAIN = "approval_chain"  # 审批链
```

### 插件系统

设计插件接口支持功能扩展：

```python
class HumanLoopPlugin:
    """插件基类"""
    
    def on_session_created(self, session):
        """会话创建时的钩子"""
        pass
    
    def on_session_completed(self, session):
        """会话完成时的钩子"""
        pass
    
    def on_session_timeout(self, session):
        """会话超时时的钩子"""
        pass

class EmailNotificationPlugin(HumanLoopPlugin):
    """邮件通知插件"""
    
    def on_session_created(self, session):
        """发送邮件通知"""
        send_email_notification(session)
```

### 国际化支持

添加多语言支持：

```python
# i18n.py
import gettext

class I18nManager:
    def __init__(self, language='zh-CN'):
        self.language = language
        self.translator = gettext.translation(
            'human_loop_mcp', 
            localedir='locales', 
            languages=[language],
            fallback=True
        )
    
    def _(self, message):
        """翻译消息"""
        return self.translator.gettext(message)

# 使用示例
i18n = I18nManager('en-US')
title = i18n._("Confirm Deployment")
```

## 版本历史

### v1.0.0 (2025-06-17)
- 初始版本发布
- 支持四种基本交互类型
- 实现 RESTful API 和 WebSocket 通信
- 提供完整的前端界面
- 包含单元测试和集成测试

### 未来版本规划

#### v1.1.0 (计划)
- 添加用户认证和授权
- 支持电子签名交互类型
- 增强安全性和审计功能
- 性能优化和缓存改进

#### v1.2.0 (计划)
- 支持审批链工作流
- 添加移动端适配
- 实现插件系统
- 国际化支持

#### v2.0.0 (计划)
- 微服务架构重构
- 支持分布式部署
- 机器学习辅助决策
- 高级分析和报告功能

## 贡献指南

### 开发环境设置

1. Fork 项目仓库
2. 创建开发分支
3. 安装开发依赖
4. 运行测试确保环境正常

### 代码规范

- 遵循 PEP 8 Python 代码规范
- 使用类型注解
- 编写单元测试
- 添加适当的文档字符串

### 提交流程

1. 创建功能分支
2. 实现功能并添加测试
3. 运行完整测试套件
4. 提交 Pull Request
5. 代码审查和合并

## 许可证

本项目采用 MIT 许可证，详见 LICENSE 文件。

## 联系方式

- 项目维护者: Manus AI Team
- 邮箱: support@manus.ai
- 文档: https://docs.manus.ai/human-loop-mcp
- 问题反馈: https://github.com/manus-ai/aicore/issues

---

*本文档由 Manus AI 自动生成，最后更新时间: 2025-06-17*

