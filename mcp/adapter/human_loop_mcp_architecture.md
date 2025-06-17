# Human-in-the-Loop MCP 架构设计文档

## 概述

Human-in-the-Loop MCP (人机交互循环模型控制协议) 是PowerAutomation系统中的一个关键适配器组件，旨在在自动化工作流的关键决策点引入人工智慧和判断。本组件参考了SmartUI MCP的GUI交互模式，提供了现代化的Web界面和强大的后端服务。

## 架构设计原则

### 1. 模块化设计
Human-in-the-Loop MCP采用模块化架构，将功能分解为独立的、可重用的组件。每个模块都有明确的职责和接口，便于维护和扩展。

### 2. 前后端分离
参考SmartUI MCP的成功实践，采用前后端分离的架构模式。后端提供RESTful API服务，前端使用现代Web技术构建用户界面，两者通过HTTP/WebSocket协议进行通信。

### 3. 异步处理
为了避免阻塞主工作流，所有人工交互都采用异步处理模式。工作流在需要人工介入时会暂停并等待，用户完成交互后通过回调机制恢复执行。

### 4. 状态管理
实现完善的状态管理机制，确保交互会话的持久性和一致性。支持会话恢复、超时处理和异常恢复。

## 系统架构

### 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                    PowerAutomation 系统                      │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────┐                │
│  │ 工作流引擎        │    │ MCP协调器        │                │
│  │                 │◄──►│                 │                │
│  └─────────────────┘    └─────────────────┘                │
│           │                       │                        │
│           ▼                       ▼                        │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │           Human-in-the-Loop MCP                        │ │
│  ├─────────────────────────────────────────────────────────┤ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │ │
│  │  │ API服务器    │  │ 会话管理器   │  │ 状态存储     │    │ │
│  │  │             │  │             │  │             │    │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘    │ │
│  │         │                 │                 │         │ │
│  │         ▼                 ▼                 ▼         │ │
│  │  ┌─────────────────────────────────────────────────────┐ │ │
│  │  │              Web前端界面                           │ │ │
│  │  └─────────────────────────────────────────────────────┘ │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 核心组件

#### 1. API服务器 (Flask-based)
基于Flask框架构建的RESTful API服务器，参考SmartUI MCP的实现模式：

- **端口配置**: 8096 (避免与现有服务冲突)
- **CORS支持**: 允许跨域请求，支持Web界面访问
- **路由设计**: RESTful风格的API端点
- **错误处理**: 统一的错误响应格式
- **日志记录**: 详细的操作日志和审计追踪

#### 2. 会话管理器
负责管理用户交互会话的生命周期：

- **会话创建**: 当工作流需要人工介入时创建新会话
- **会话跟踪**: 维护会话状态和上下文信息
- **超时处理**: 自动处理超时会话，提供默认行为
- **并发管理**: 支持多用户同时进行交互

#### 3. 状态存储
持久化存储交互状态和历史记录：

- **Redis缓存**: 用于快速访问的会话状态
- **SQLite数据库**: 用于持久化存储的历史记录
- **状态同步**: 确保多实例间的状态一致性

#### 4. Web前端界面
现代化的Web用户界面，提供直观的交互体验：

- **响应式设计**: 支持桌面和移动设备
- **实时更新**: 通过WebSocket实现实时状态更新
- **交互组件**: 丰富的交互组件库
- **主题支持**: 支持明暗主题切换

## 交互流程设计

### 标准交互流程

1. **触发阶段**
   - 工作流执行到需要人工介入的节点
   - 调用Human-in-the-Loop MCP的API接口
   - 创建新的交互会话

2. **展示阶段**
   - 在Web界面显示交互请求
   - 提供上下文信息和可选操作
   - 等待用户响应

3. **交互阶段**
   - 用户通过Web界面进行操作
   - 实时验证用户输入
   - 提供操作反馈

4. **完成阶段**
   - 收集用户的决策结果
   - 更新会话状态
   - 通知工作流继续执行

### 交互类型

#### 1. 确认对话框
用于需要用户确认的场景：

```json
{
  "type": "confirmation",
  "title": "确认操作",
  "message": "是否继续执行部署操作？",
  "options": ["确认", "取消"],
  "default": "取消",
  "timeout": 300
}
```

#### 2. 选择对话框
用于需要用户从多个选项中选择的场景：

```json
{
  "type": "selection",
  "title": "选择部署环境",
  "message": "请选择目标部署环境",
  "options": [
    {"value": "dev", "label": "开发环境"},
    {"value": "staging", "label": "测试环境"},
    {"value": "prod", "label": "生产环境"}
  ],
  "multiple": false,
  "timeout": 600
}
```

#### 3. 文本输入
用于需要用户输入文本信息的场景：

```json
{
  "type": "text_input",
  "title": "输入配置参数",
  "fields": [
    {
      "name": "database_url",
      "label": "数据库连接URL",
      "type": "text",
      "required": true,
      "validation": "^postgresql://.*"
    },
    {
      "name": "max_connections",
      "label": "最大连接数",
      "type": "number",
      "default": 100,
      "min": 1,
      "max": 1000
    }
  ],
  "timeout": 900
}
```

#### 4. 文件上传
用于需要用户上传文件的场景：

```json
{
  "type": "file_upload",
  "title": "上传配置文件",
  "accept": [".json", ".yaml", ".yml"],
  "max_size": "10MB",
  "multiple": false,
  "timeout": 1200
}
```

## 技术实现细节

### 后端实现 (Python/Flask)

#### API端点设计

```python
# 主要API端点
@app.route('/api/sessions', methods=['POST'])
def create_session():
    """创建新的交互会话"""
    pass

@app.route('/api/sessions/<session_id>', methods=['GET'])
def get_session(session_id):
    """获取会话信息"""
    pass

@app.route('/api/sessions/<session_id>/respond', methods=['POST'])
def respond_session(session_id):
    """提交用户响应"""
    pass

@app.route('/api/sessions/<session_id>/status', methods=['GET'])
def get_session_status(session_id):
    """获取会话状态"""
    pass
```

#### 会话管理实现

```python
class SessionManager:
    def __init__(self):
        self.active_sessions = {}
        self.redis_client = redis.Redis()
        
    def create_session(self, interaction_data):
        """创建新会话"""
        session_id = str(uuid.uuid4())
        session = InteractionSession(
            session_id=session_id,
            interaction_type=interaction_data['type'],
            data=interaction_data,
            created_at=datetime.now(),
            timeout=interaction_data.get('timeout', 300)
        )
        
        self.active_sessions[session_id] = session
        self.redis_client.setex(
            f"session:{session_id}",
            session.timeout,
            json.dumps(session.to_dict())
        )
        
        return session
```

### 前端实现 (HTML/CSS/JavaScript)

#### 主界面结构

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Human-in-the-Loop 交互界面</title>
    <link rel="stylesheet" href="/static/css/main.css">
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>PowerAutomation 人机交互</h1>
            <div class="status-indicator" id="connectionStatus">
                <span class="status-dot"></span>
                <span class="status-text">已连接</span>
            </div>
        </header>
        
        <main class="main-content">
            <div class="session-list" id="sessionList">
                <!-- 会话列表 -->
            </div>
            
            <div class="interaction-panel" id="interactionPanel">
                <!-- 交互面板 -->
            </div>
        </main>
    </div>
    
    <script src="/static/js/main.js"></script>
</body>
</html>
```

#### JavaScript交互逻辑

```javascript
class HumanLoopClient {
    constructor() {
        this.apiBase = '/api';
        this.websocket = null;
        this.activeSessions = new Map();
        
        this.initWebSocket();
        this.loadActiveSessions();
    }
    
    initWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;
        
        this.websocket = new WebSocket(wsUrl);
        this.websocket.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleWebSocketMessage(data);
        };
    }
    
    async respondToSession(sessionId, response) {
        try {
            const result = await fetch(`${this.apiBase}/sessions/${sessionId}/respond`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(response)
            });
            
            if (result.ok) {
                this.removeSession(sessionId);
                this.showNotification('响应已提交', 'success');
            }
        } catch (error) {
            this.showNotification('提交失败: ' + error.message, 'error');
        }
    }
}
```

## 配置和部署

### MCP配置文件

根据PowerAutomation目录规范，Human-in-the-Loop MCP的配置应该放在 `/mcp/adapter/human_loop_mcp/config/` 目录下：

#### human_loop_mcp_config.yaml

```yaml
# Human-in-the-Loop MCP 配置文件
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
  default_timeout: 300  # 5分钟
  max_timeout: 3600     # 1小时
  cleanup_interval: 60  # 清理间隔(秒)
  
ui:
  theme: "light"
  language: "zh-CN"
  auto_refresh: true
  refresh_interval: 5   # 秒
  
logging:
  level: "INFO"
  file: "logs/human_loop_mcp.log"
  max_size: "10MB"
  backup_count: 5
  
security:
  enable_auth: false
  session_secret: "your-secret-key-here"
  cors_origins: ["*"]
  
integration:
  mcp_coordinator_url: "http://localhost:8090"
  workflow_callback_timeout: 30
```

#### 端口分配说明

根据现有系统的端口分配：
- 需求分析MCP: 8094
- 架构设计MCP: 8095
- **Human-in-the-Loop MCP: 8096** (新分配)

### 部署脚本

#### start_human_loop_mcp.sh

```bash
#!/bin/bash

# Human-in-the-Loop MCP 启动脚本

# 设置环境变量
export PYTHONPATH="/home/ubuntu/aicore0615:$PYTHONPATH"
export HUMAN_LOOP_CONFIG="/home/ubuntu/aicore0615/mcp/adapter/human_loop_mcp/config/human_loop_mcp_config.yaml"

# 创建必要的目录
mkdir -p /home/ubuntu/aicore0615/mcp/adapter/human_loop_mcp/logs
mkdir -p /home/ubuntu/aicore0615/mcp/adapter/human_loop_mcp/data

# 启动服务
cd /home/ubuntu/aicore0615/mcp/adapter/human_loop_mcp
python3 src/human_loop_server.py

echo "Human-in-the-Loop MCP 已启动在端口 8096"
```

## 与现有系统的集成

### 更新configurable_review_workflow.py

需要修改现有的工作流配置，将Human-in-the-Loop MCP的URL指向正确的端口：

```python
# 修改前
self.human_loop_mcp_url = "http://localhost:8094"  # 错误：这是需求分析MCP

# 修改后
self.human_loop_mcp_url = "http://localhost:8096"  # 正确：Human-in-the-Loop MCP
```

### MCP协调器注册

在MCP协调器中注册Human-in-the-Loop MCP：

```python
# mcp/adapter/mcp_service_registrar.py
SERVICES = {
    # ... 现有服务
    "human_loop_mcp": {
        "name": "Human-in-the-Loop MCP",
        "port": 8096,
        "endpoint": "http://localhost:8096",
        "health_check": "/api/health",
        "type": "adapter",
        "status": "active"
    }
}
```

## 安全性考虑

### 1. 身份认证
- 支持可选的身份认证机制
- 集成现有的用户管理系统
- 支持JWT令牌认证

### 2. 权限控制
- 基于角色的访问控制(RBAC)
- 细粒度的操作权限
- 审计日志记录

### 3. 数据安全
- 敏感数据加密存储
- HTTPS传输加密
- 会话数据自动清理

### 4. 输入验证
- 严格的输入验证和清理
- 防止XSS和SQL注入攻击
- 文件上传安全检查

## 监控和运维

### 1. 健康检查
提供标准的健康检查端点：

```python
@app.route('/api/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0",
        "active_sessions": len(session_manager.active_sessions)
    })
```

### 2. 指标监控
- 活跃会话数量
- 响应时间统计
- 错误率监控
- 资源使用情况

### 3. 日志管理
- 结构化日志格式
- 日志轮转和归档
- 错误日志告警

## 测试策略

### 1. 单元测试
- API端点测试
- 会话管理测试
- 数据验证测试

### 2. 集成测试
- 与工作流引擎的集成测试
- 数据库操作测试
- WebSocket通信测试

### 3. 端到端测试
- 完整交互流程测试
- 超时处理测试
- 并发用户测试

### 4. 性能测试
- 负载测试
- 压力测试
- 内存泄漏测试

## 扩展性设计

### 1. 插件系统
支持自定义交互组件的插件机制：

```python
class InteractionPlugin:
    def __init__(self, name, version):
        self.name = name
        self.version = version
    
    def render(self, data):
        """渲染交互界面"""
        pass
    
    def validate(self, response):
        """验证用户响应"""
        pass
    
    def process(self, response):
        """处理用户响应"""
        pass
```

### 2. 主题系统
支持自定义UI主题和样式。

### 3. 国际化支持
支持多语言界面和消息。

### 4. API版本控制
支持API版本管理和向后兼容。

## 总结

Human-in-the-Loop MCP的架构设计充分考虑了PowerAutomation系统的现有架构和需求，参考了SmartUI MCP的成功实践，提供了完整的人机交互解决方案。通过模块化设计、前后端分离、异步处理和完善的状态管理，确保了系统的可靠性、可扩展性和用户体验。

该架构不仅满足了当前的功能需求，还为未来的扩展和优化留下了充足的空间。通过标准化的配置管理、完善的测试策略和监控机制，确保了系统的可维护性和运维友好性。

