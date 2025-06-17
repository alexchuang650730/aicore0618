# PowerAutomation 远程部署完整指南

## 🎯 部署概述

本文档提供PowerAutomation系统到远程服务器 **98.81.255.168:5001** 的完整部署指南。

### 📋 部署信息
- **目标服务器**: 98.81.255.168
- **主服务端口**: 5001
- **SSH密钥**: alexchuang.pem
- **部署路径**: /opt/powerautomation
- **用户**: ubuntu

## 🏗️ 系统架构

### 服务端口分配
| 服务 | 端口 | 描述 |
|------|------|------|
| SmartUI DevOps API Server | 5001 | 主API服务器 |
| Test Manager MCP | 8097 | 测试管理服务 |
| Release Manager MCP | 8096 | 发布管理服务 |
| Operations Workflow MCP | 8090 | 运维监控服务 |

### 核心组件
1. **SmartUI DevOps Dashboard** - Web前端界面
2. **DevOps API Server** - 后端API服务
3. **三个Workflow MCP** - 核心工作流服务
4. **测试框架** - 完整的测试体系

## 🚀 快速部署

### 1. 一键部署
```bash
cd /opt/powerautomation
./deploy_remote.sh
```

### 2. 部署过程
部署脚本将自动执行以下步骤：
1. ✅ 检查本地环境
2. ✅ 测试SSH连接
3. ✅ 检查远程环境
4. ✅ 创建目录结构
5. ✅ 备份现有部署
6. ✅ 上传项目文件
7. ✅ 安装Python依赖
8. ✅ 停止现有服务
9. ✅ 启动新服务
10. ✅ 验证部署状态

### 3. 部署验证
部署完成后，访问以下地址验证：
- **主界面**: http://98.81.255.168:5001
- **API状态**: http://98.81.255.168:5001/api/status
- **Workflow状态**: http://98.81.255.168:5001/api/workflows/status

## 🛠️ 服务管理

### 管理脚本使用
```bash
# 查看服务状态
./manage_remote.sh status

# 启动所有服务
./manage_remote.sh start

# 停止所有服务
./manage_remote.sh stop

# 重启所有服务
./manage_remote.sh restart

# 查看日志
./manage_remote.sh logs

# 查看特定服务日志
./manage_remote.sh logs smartui_api

# 测试连接
./manage_remote.sh test
```

### 手动SSH管理
```bash
# 连接到远程服务器
ssh -i /opt/powerautomation/alexchuang.pem ubuntu@98.81.255.168

# 查看服务进程
ps aux | grep smartui

# 查看端口占用
netstat -tlnp | grep -E "(5001|8090|8096|8097)"

# 查看日志
tail -f /opt/powerautomation/logs/*.log
```

## 📊 功能测试

### 1. API端点测试
```bash
# 主API状态
curl http://98.81.255.168:5001/api/status

# Workflow状态
curl http://98.81.255.168:5001/api/workflows/status

# 聊天功能
curl -X POST http://98.81.255.168:5001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"我要开发贪吃蛇游戏"}'
```

### 2. DevOps流水线测试
```bash
# 测试按钮
curl -X POST http://98.81.255.168:5001/api/button/test \
  -H "Content-Type: application/json" \
  -d '{"project_info":{"name":"测试项目","type":"game"}}'

# 部署按钮
curl -X POST http://98.81.255.168:5001/api/button/deploy \
  -H "Content-Type: application/json" \
  -d '{"project_info":{"name":"测试项目","type":"game"}}'

# 运维按钮
curl -X POST http://98.81.255.168:5001/api/button/monitor \
  -H "Content-Type: application/json" \
  -d '{"project_info":{"name":"测试项目","type":"game"}}'

# 完整流水线
curl -X POST http://98.81.255.168:5001/api/devops/full-pipeline \
  -H "Content-Type: application/json" \
  -d '{"project_info":{"name":"贪吃蛇游戏","type":"game","complexity":"simple"}}'
```

### 3. 各MCP服务测试
```bash
# Test Manager MCP
curl http://98.81.255.168:8097/api/status

# Release Manager MCP
curl http://98.81.255.168:8096/api/status

# Operations Workflow MCP
curl http://98.81.255.168:8090/api/status
```

## 🔧 配置文件

### 部署配置 (deploy_config.sh)
```bash
TARGET_SERVER="98.81.255.168"
TARGET_PORT="5001"
SSH_KEY="/opt/powerautomation/alexchuang.pem"
SSH_USER="ubuntu"
REMOTE_DEPLOY_PATH="/opt/powerautomation"
```

### Workflow端点配置
```python
WORKFLOW_ENDPOINTS = {
    "test_manager": "http://98.81.255.168:8097",
    "release_manager": "http://98.81.255.168:8096", 
    "operations_workflow": "http://98.81.255.168:8090"
}
```

## 📁 文件结构

### 本地文件
```
/opt/powerautomation/
├── alexchuang.pem                    # SSH密钥
├── deploy_config.sh                  # 部署配置
├── deploy_remote.sh                  # 部署脚本
├── manage_remote.sh                  # 管理脚本
├── smartui_devops_api_server_remote.py  # 远程版API服务器
├── smartui_devops_dashboard.html     # Web界面
└── mcp/workflow/                     # MCP服务
    ├── test_manager_mcp/
    ├── release_manager_mcp/
    └── operations_workflow_mcp/
```

### 远程文件
```
/opt/powerautomation/
├── smartui_devops_api_server.py      # 主API服务器
├── smartui_devops_dashboard.html     # Web界面
├── mcp/workflow/                     # MCP服务
├── test/framework/                   # 测试框架
├── logs/                            # 日志文件
└── start_smartui_devops.sh          # 启动脚本
```

## 🔍 故障排除

### 常见问题

#### 1. SSH连接失败
```bash
# 检查密钥权限
chmod 600 /opt/powerautomation/alexchuang.pem

# 测试SSH连接
ssh -i /opt/powerautomation/alexchuang.pem ubuntu@98.81.255.168 "echo 'SSH连接成功'"
```

#### 2. 服务启动失败
```bash
# 检查Python依赖
./manage_remote.sh logs

# 手动启动服务
ssh -i /opt/powerautomation/alexchuang.pem ubuntu@98.81.255.168
cd /opt/powerautomation
python3 smartui_devops_api_server.py
```

#### 3. 端口占用
```bash
# 检查端口占用
./manage_remote.sh status

# 停止冲突服务
./manage_remote.sh stop
```

#### 4. API调用失败
```bash
# 检查服务状态
./manage_remote.sh test

# 查看API日志
./manage_remote.sh logs smartui_api
```

### 日志文件位置
- **SmartUI API**: `/opt/powerautomation/logs/smartui_api.log`
- **Test Manager**: `/opt/powerautomation/logs/test_manager.log`
- **Release Manager**: `/opt/powerautomation/logs/release_manager.log`
- **Operations Workflow**: `/opt/powerautomation/logs/operations_workflow.log`

## 🔄 更新部署

### 更新流程
1. 修改本地代码
2. 运行部署脚本：`./deploy_remote.sh`
3. 验证更新：`./manage_remote.sh test`

### 回滚操作
```bash
# SSH到远程服务器
ssh -i /opt/powerautomation/alexchuang.pem ubuntu@98.81.255.168

# 查看备份
ls -la /opt/powerautomation_backup/

# 恢复备份
sudo cp -r /opt/powerautomation_backup/powerautomation_backup_YYYYMMDD_HHMMSS/* /opt/powerautomation/

# 重启服务
cd /opt/powerautomation && ./start_smartui_devops.sh
```

## 🔐 安全配置

### 防火墙设置
```bash
# 开放必要端口
sudo ufw allow 5001
sudo ufw allow 8090
sudo ufw allow 8096
sudo ufw allow 8097
```

### SSL配置 (可选)
如需HTTPS访问，可配置反向代理：
```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📈 监控和维护

### 系统监控
- **CPU使用率**: 通过Operations Workflow MCP监控
- **内存使用**: 系统自动监控
- **磁盘空间**: 定期检查日志文件大小
- **网络连接**: API健康检查

### 定期维护
1. **日志清理**: 定期清理旧日志文件
2. **备份验证**: 验证自动备份完整性
3. **安全更新**: 定期更新系统和依赖
4. **性能优化**: 根据监控数据优化配置

## 📞 支持联系

如遇到部署问题，请：
1. 查看日志文件获取详细错误信息
2. 使用管理脚本进行基础故障排除
3. 联系PowerAutomation技术支持团队

---

**版本**: v3.0.0  
**更新时间**: 2025-06-17  
**部署目标**: 98.81.255.168:5001  
**状态**: ✅ 生产就绪

