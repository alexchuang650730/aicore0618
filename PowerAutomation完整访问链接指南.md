# PowerAutomation 完整访问链接指南

## 🌐 **主要服务访问地址**

### 🎯 **核心服务 (98.81.255.168)**

#### **1. 主界面 - AI智能开发平台**
- **🏠 主页面**: http://98.81.255.168:5001
- **🤖 API状态**: http://98.81.255.168:5001/api/status
- **💬 聊天API**: http://98.81.255.168:5001/api/chat
- **功能**: AI代码生成、三个智能按钮、项目下载

#### **2. 三个专业MCP服务**
- **🧪 Test Manager MCP**: http://98.81.255.168:8097
  - 状态检查: http://98.81.255.168:8097/api/status
  - 功能: 智能测试管理和执行

- **🚀 Release Manager MCP**: http://98.81.255.168:8096
  - 状态检查: http://98.81.255.168:8096/api/status
  - 功能: 智能部署管理和发布验证

- **📊 Operations Workflow MCP**: http://98.81.255.168:8090
  - 状态检查: http://98.81.255.168:8090/api/status
  - 功能: 智能运维工作流管理

---

## 🔧 **扩展服务**

#### **3. 管理和协调服务**
- **🎛️ MCP Coordinator**: http://98.81.255.168:8089
  - 功能: 中央协调器，管理所有MCP通信

- **💻 KILOCODE MCP**: http://98.81.255.168:8080
  - 功能: 代码生成和管理服务

- **⚙️ Admin Service**: http://98.81.255.168:5000
  - 功能: 系统管理和监控

#### **4. 其他专业服务**
- **📱 Smart UI MCP**: http://98.81.255.168:8090 (与Operations重叠)
- **🔗 Webhook Service**: 运行在后台
- **📈 Monitoring Services**: 集成在各个MCP中

---

## 🎮 **使用方式**

### 🌐 **方式一：Web界面访问**
```
直接访问: http://98.81.255.168:5001
```
**功能**:
- 🤖 AI智能代码生成
- 📦 下载完整代码
- 🎮 在线预览项目
- 📚 查看技术文档

### 🔌 **方式二：API直接调用**

#### **生成项目代码**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"message":"我要开发贪吃蛇游戏"}' \
  http://98.81.255.168:5001/api/chat
```

#### **检查系统状态**
```bash
curl http://98.81.255.168:5001/api/status
```

#### **检查MCP服务状态**
```bash
# Test Manager
curl http://98.81.255.168:8097/api/status

# Release Manager  
curl http://98.81.255.168:8096/api/status

# Operations Workflow
curl http://98.81.255.168:8090/api/status
```

### 🔐 **方式三：SSH隧道访问**
如果Web界面访问有问题，可以使用SSH隧道：
```bash
ssh -L 5001:localhost:5001 -i alexchuang.pem ec2-user@98.81.255.168
# 然后访问 http://localhost:5001
```

---

## 📊 **服务状态总览**

| 服务名称 | 端口 | 状态 | 主要功能 |
|---------|------|------|----------|
| 主界面 | 5001 | ✅ 运行中 | AI代码生成、按钮交互 |
| Test Manager MCP | 8097 | ✅ 运行中 | 智能测试管理 |
| Release Manager MCP | 8096 | ✅ 运行中 | 智能部署管理 |
| Operations MCP | 8090 | ✅ 运行中 | 运维工作流管理 |
| MCP Coordinator | 8089 | 🔄 检查中 | 中央协调器 |
| KILOCODE MCP | 8080 | 🔄 检查中 | 代码管理服务 |
| Admin Service | 5000 | 🔄 检查中 | 系统管理 |

---

## 🎯 **核心功能链接**

### 🤖 **AI代码生成**
- **主入口**: http://98.81.255.168:5001
- **API端点**: http://98.81.255.168:5001/api/chat
- **支持项目**: 游戏、网站、应用、工具等

### 📦 **三个智能按钮**
1. **下载完整代码** - 获取所有项目文件
2. **在线预览** - 实时查看项目效果  
3. **查看文档** - 技术文档和说明

### 🔄 **DevOps流水线**
- **测试**: http://98.81.255.168:8097 (Test Manager)
- **部署**: http://98.81.255.168:8096 (Release Manager)
- **运维**: http://98.81.255.168:8090 (Operations)

---

## 🚀 **快速开始**

### 1️⃣ **立即体验**
访问: http://98.81.255.168:5001
输入: "我要开发一个计算器"
点击: "🤖 生成项目"

### 2️⃣ **下载代码**
生成项目后，点击 "📦 下载完整代码"

### 3️⃣ **查看预览**
点击 "🎮 在线预览" 查看项目效果

### 4️⃣ **阅读文档**
点击 "📚 查看文档" 了解技术细节

---

## 🔧 **故障排除**

### ❓ **如果主界面无法访问**
1. 检查API状态: `curl http://98.81.255.168:5001/api/status`
2. 使用SSH隧道: `ssh -L 5001:localhost:5001 -i alexchuang.pem ec2-user@98.81.255.168`
3. 直接使用API调用

### ❓ **如果按钮无响应**
1. 刷新页面重试
2. 检查浏览器控制台错误
3. 使用API直接调用功能

### ❓ **如果MCP服务无响应**
1. 检查各个MCP状态链接
2. 联系管理员重启服务
3. 查看服务日志

---

## 📞 **技术支持**

### 🔗 **重要链接**
- **主服务器**: 98.81.255.168
- **SSH访问**: `ssh -i alexchuang.pem ec2-user@98.81.255.168`
- **服务目录**: `/opt/powerautomation`

### 📋 **服务管理**
```bash
# 检查所有服务状态
ps aux | grep python | grep -E "(5001|8090|8096|8097)"

# 重启主界面
cd /opt/powerautomation
python3 smartui_button_fix_server.py

# 重启MCP服务
python3 mcp/workflow/test_manager_mcp/test_manager_mcp_server.py &
python3 mcp/workflow/release_manager_mcp/release_manager_mcp_server.py &
```

---

## 🎉 **总结**

PowerAutomation现在提供完整的AI驱动开发平台，包括：

✅ **主界面**: http://98.81.255.168:5001  
✅ **三个MCP服务**: 8097, 8096, 8090  
✅ **完整API**: 支持所有功能调用  
✅ **智能按钮**: 下载、预览、文档  

**立即开始使用您的AI开发助手！** 🚀

---

**更新时间**: 2025-06-17 16:50  
**服务版本**: 3.0.0-fixed  
**状态**: 完全可用

