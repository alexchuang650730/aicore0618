# PowerAutomation系统启动指南

## 🚀 **快速启动**

### **1. 启动Enhanced Test Manager MCP**
```bash
cd /home/ubuntu/aicore0615/mcp/workflow/test_manager_mcp
python3 test_manager_mcp.py &
```
- 服务地址: http://localhost:8097
- 健康检查: `curl http://localhost:8097/health`

### **2. 启动SmartUI系统**
```bash
cd /home/ubuntu/aicore0615/smartui_fixed
env PYTHONPATH=/home/ubuntu/aicore0615 python3 api_server.py &
```
- 服务地址: http://localhost:5001
- 状态检查: `curl http://localhost:5001/api/status`

### **3. 启动Product Orchestrator V3**
```bash
cd /home/ubuntu/aicore0615
env PYTHONPATH=/home/ubuntu/aicore0615 python3 -c "
from mcp.coordinator.workflow_collaboration.product_orchestrator_v3 import ProductOrchestratorV3
import asyncio
orchestrator = ProductOrchestratorV3()
asyncio.run(orchestrator.start_server())
" &
```
- WebSocket地址: ws://localhost:5002

## 📋 **API使用指南**

### **智能测试策略生成**
```bash
curl -X POST http://localhost:8097/api/test/strategy \
  -H "Content-Type: application/json" \
  -d '{
    "project_info": {
      "name": "My Project",
      "type": "web_app",
      "complexity": "medium"
    }
  }'
```

### **智能测试用例生成**
```bash
curl -X POST http://localhost:8097/api/test/cases \
  -H "Content-Type: application/json" \
  -d '{
    "strategy": {...},
    "requirements": {...}
  }'
```

### **完整智能测试周期**
```bash
curl -X POST http://localhost:8097/api/test/intelligent-cycle \
  -H "Content-Type: application/json" \
  -d '{
    "project_info": {
      "name": "Demo Project",
      "type": "web_app",
      "complexity": "medium"
    },
    "execution_config": {
      "mode": "mixed",
      "parallel_limit": 3
    }
  }'
```

## 🔧 **故障排除**

### **常见问题**

1. **端口占用**
   ```bash
   # 检查端口占用
   netstat -tlnp | grep :8097
   # 终止占用进程
   kill <PID>
   ```

2. **Python路径问题**
   ```bash
   export PYTHONPATH=/home/ubuntu/aicore0615:$PYTHONPATH
   ```

3. **权限问题**
   ```bash
   sudo mkdir -p /opt/powerautomation/test/logs
   sudo chown -R ubuntu:ubuntu /opt/powerautomation
   ```

### **日志查看**
```bash
# Test Manager MCP日志
tail -f /opt/powerautomation/test/logs/test_manager.log

# SmartUI日志
tail -f /home/ubuntu/aicore0615/smartui_fixed/smartui.log
```

## 📊 **系统监控**

### **健康检查脚本**
```bash
#!/bin/bash
echo "=== PowerAutomation系统状态检查 ==="

echo "1. Enhanced Test Manager MCP:"
curl -s http://localhost:8097/health | python3 -m json.tool

echo -e "\n2. SmartUI系统:"
curl -s http://localhost:5001/api/status | python3 -m json.tool

echo -e "\n3. 进程状态:"
ps aux | grep -E "(test_manager|api_server|orchestrator)" | grep -v grep
```

## 🎯 **使用建议**

### **最佳实践**
1. **按顺序启动**: Test Manager MCP → SmartUI → Product Orchestrator V3
2. **健康检查**: 每个服务启动后都进行健康检查
3. **日志监控**: 定期查看日志确保系统正常运行
4. **资源监控**: 监控CPU和内存使用情况

### **性能优化**
1. **并行执行**: 使用mixed模式获得最佳性能
2. **资源限制**: 根据系统资源调整parallel_limit
3. **缓存利用**: 重复项目可复用之前的策略和用例

## 🔄 **备份与恢复**

### **备份重要数据**
```bash
# 备份配置和数据
tar -czf powerautomation_backup_$(date +%Y%m%d).tar.gz \
  /home/ubuntu/aicore0615/mcp/workflow/test_manager_mcp \
  /home/ubuntu/aicore0615/smartui_fixed \
  /opt/powerautomation
```

### **恢复系统**
```bash
# 从备份恢复
tar -xzf powerautomation_backup_YYYYMMDD.tar.gz -C /
```

这个启动指南确保了PowerAutomation系统的稳定运行和高效使用。

