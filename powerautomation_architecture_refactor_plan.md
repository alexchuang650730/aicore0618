# PowerAutomation 三层架构重构计划

## 🏗️ **当前架构问题分析**

### **现状**
```
coding_plugin_orchestrator (产品级) → mcp/adapter组件 (组件级)
```

### **正确架构**
```
coding_plugin_orchestrator (产品级) → workflow orchestrator (工作流级) → mcp/adapter组件 (组件级)
```

## 🎯 **重构目标**

### **1. 创建标准的Workflow Orchestrator中间层**
- 位置: `/home/ubuntu/aicore0615/mcp/workflow/workflow_orchestrator/`
- 功能: 统一的工作流编排服务
- 端口: 8090 (工作流级服务)

### **2. 重构Test Manager MCP为纯组件级服务**
- 位置: `/home/ubuntu/aicore0615/mcp/adapter/test_manager_mcp/`
- 功能: 纯粹的测试管理组件服务
- 端口: 8094 (组件级服务)

### **3. 修改产品级服务调用方式**
- coding_plugin_orchestrator → workflow_orchestrator
- 其他产品也可以通过workflow_orchestrator调用组件

## 📋 **实施步骤**

### **Phase 1: 创建Workflow Orchestrator**
1. 基于现有的 `/home/ubuntu/aicore0615/mcp/coordinator/workflow_collaboration/workflow_orchestrator.py`
2. 扩展为完整的工作流编排服务
3. 支持多种工作流模板
4. 提供统一的MCP组件调用接口

### **Phase 2: 重构Test Manager MCP**
1. 简化为纯组件级服务
2. 移除产品级逻辑
3. 专注于测试管理核心功能

### **Phase 3: 修改调用链路**
1. coding_plugin_orchestrator → workflow_orchestrator
2. workflow_orchestrator → test_manager_mcp
3. 验证端到端调用

### **Phase 4: 验证其他产品调用**
1. 确保其他产品可以通过workflow_orchestrator调用
2. 测试多产品并发调用
3. 验证组件复用性

## 🔧 **技术实现**

### **Workflow Orchestrator API设计**
```
POST /api/workflow/execute
GET  /api/workflow/{id}/status
GET  /api/workflow/{id}/result
POST /api/workflow/{id}/cancel
```

### **Test Manager MCP API保持**
```
POST /api/test/strategy
POST /api/test/cases  
POST /api/test/execute
GET  /api/test/status/{id}
GET  /api/test/report/{id}
```

### **调用流程**
```
1. Product → Workflow Orchestrator (提交工作流请求)
2. Workflow Orchestrator → MCP Components (按阶段调用)
3. MCP Components → Workflow Orchestrator (返回结果)
4. Workflow Orchestrator → Product (返回最终结果)
```

