# 🌐 PowerAutomation SSH隧道访问指南

## 🎯 **推荐解决方案：SSH隧道**

由于Web界面存在504超时问题，但API功能完全正常，最佳解决方案是使用SSH隧道。

### **🔧 单服务隧道** (最简单)

```bash
# 创建主服务隧道
ssh -L 8080:localhost:5001 -i alexchuang.pem ec2-user@98.81.255.168

# 访问链接
http://localhost:8080
```

### **🔧 完整服务隧道** (推荐)

```bash
# 创建所有服务的隧道
ssh -L 8080:localhost:5001 \
    -L 8090:localhost:8090 \
    -L 8096:localhost:8096 \
    -L 8097:localhost:8097 \
    -i alexchuang.pem ec2-user@98.81.255.168

# 保持连接运行，然后在浏览器访问：
```

**访问链接**：
- **主界面**: http://localhost:8080
- **Operations MCP**: http://localhost:8090  
- **Release Manager MCP**: http://localhost:8096
- **Test Manager MCP**: http://localhost:8097

### **🔧 后台运行隧道**

```bash
# 后台运行隧道
ssh -f -N -L 8080:localhost:5001 \
    -L 8090:localhost:8090 \
    -L 8096:localhost:8096 \
    -L 8097:localhost:8097 \
    -i alexchuang.pem ec2-user@98.81.255.168

# 检查隧道状态
ps aux | grep ssh
```

## 🎮 **使用步骤**

### **1. 建立隧道连接**
```bash
ssh -L 8080:localhost:5001 -i alexchuang.pem ec2-user@98.81.255.168
```

### **2. 访问本地界面**
打开浏览器访问：http://localhost:8080

### **3. 使用完整功能**
- ✅ AI代码生成
- ✅ 三个智能按钮
- ✅ 完整的7步工作流
- ✅ 实时预览和下载

### **4. 关闭隧道**
在SSH会话中按 `Ctrl+C` 或 `exit`

## 🔌 **API直接访问** (备选方案)

如果不想使用SSH隧道，可以直接使用API：

### **生成项目**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"message":"我要开发一个在线商城"}' \
  http://98.81.255.168:5001/api/chat
```

### **检查状态**
```bash
curl http://98.81.255.168:5001/api/status
```

## 🛠️ **API工具推荐**

### **Postman**
1. 创建新的Collection
2. 添加POST请求到 `http://98.81.255.168:5001/api/chat`
3. 设置Header: `Content-Type: application/json`
4. 设置Body: `{"message": "您的项目需求"}`

### **Insomnia**
1. 创建新的Request
2. 设置为POST方法
3. URL: `http://98.81.255.168:5001/api/chat`
4. 添加JSON Body

### **Thunder Client** (VS Code)
1. 安装Thunder Client插件
2. 创建新请求
3. 配置API端点和参数

## 🎯 **功能验证**

### **测试AI代码生成**
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"message":"创建一个简单的计算器"}' \
  http://98.81.255.168:5001/api/chat
```

### **测试MCP服务**
```bash
# Test Manager MCP
curl http://98.81.255.168:8097/api/status

# Release Manager MCP  
curl http://98.81.255.168:8096/api/status

# Operations MCP
curl http://98.81.255.168:8090/api/status
```

## 🎉 **总结**

**PowerAutomation系统功能完全正常！**

- ✅ **SSH隧道方案** - 完整Web界面体验
- ✅ **API直接调用** - 所有功能可用
- ✅ **7个专业工作流** - 端到端开发流程
- ✅ **三个智能按钮** - 下载、预览、文档

**推荐使用SSH隧道访问，获得最佳体验！** 🚀

