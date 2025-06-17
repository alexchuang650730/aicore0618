# PowerAutomation 三个专业MCP服务详细说明

## 🎯 三个专业MCP服务概览

PowerAutomation系统部署了三个核心的专业MCP（Model Control Protocol）服务，构成完整的DevOps自动化流水线：

### 1️⃣ **Test Manager MCP** (端口8097)
### 2️⃣ **Release Manager MCP** (端口8096)  
### 3️⃣ **Operations Workflow MCP** (端口8090)

---

## 🧪 **Test Manager MCP** - 智能测试管理器

### 📍 **服务信息**
- **端口**: 8097
- **服务ID**: test_manager_mcp
- **主要职责**: 统一测试管理和执行

### 🔧 **核心功能**

#### **1. 智能测试发现**
- 自动扫描项目中的测试文件
- 支持多种测试框架（unittest、pytest、jest等）
- 智能识别测试用例和测试套件
- 动态生成测试执行计划

#### **2. 测试执行管理**
- 并行测试执行
- 测试进度实时监控
- 失败测试自动重试
- 测试环境隔离

#### **3. 测试报告生成**
- 详细的测试结果报告
- HTML/JSON格式输出
- 测试覆盖率统计
- 性能指标分析

#### **4. 错误修复建议**
- 测试失败原因分析
- 自动化错误修复建议
- 代码质量检查
- 最佳实践推荐

### 🔗 **API端点**
```
GET  /api/status              - 服务状态
POST /mcp/request             - MCP请求处理
POST /api/discover_tests      - 测试发现
POST /api/run_tests          - 执行测试
GET  /api/test_reports       - 获取测试报告
```

### 📊 **集成的测试框架**
- **Test Discovery** - 智能测试发现
- **Test Runner** - 高性能测试执行器
- **Test Reporter** - 多格式报告生成
- **Test Scheduler** - 测试调度管理
- **Error Fixer** - 自动错误修复

---

## 🚀 **Release Manager MCP** - 智能发布管理器

### 📍 **服务信息**
- **端口**: 8096
- **服务ID**: release_manager_mcp
- **主要职责**: 统一部署管理和发布验证

### 🔧 **核心功能**

#### **1. 部署管理**
- 多环境部署支持（开发/测试/生产）
- 蓝绿部署策略
- 滚动更新机制
- 回滚功能

#### **2. 服务发现**
- 自动发现可部署服务
- 服务依赖关系分析
- 健康检查配置
- 负载均衡设置

#### **3. 部署验证**
- 部署前环境检查
- 部署后功能验证
- 性能基准测试
- 安全扫描

#### **4. 问题修复**
- 部署失败自动诊断
- 智能回滚决策
- 配置问题修复
- 依赖冲突解决

### 🔗 **API端点**
```
GET  /api/status                    - 服务状态
POST /mcp/request                   - MCP请求处理
POST /api/deploy                    - 执行部署
POST /api/deployment_verification  - 部署验证
GET  /api/deployment_status        - 部署状态
POST /api/rollback                  - 回滚操作
```

### 🎯 **标准端口分配管理**
- **MCP Coordinator**: 8089
- **Operations Workflow**: 8090
- **GitHub MCP**: 8091
- **Development Intervention**: 8092
- **Coding Workflow**: 8093
- **Requirements Analysis**: 8094
- **Architecture Design**: 8095
- **Release Manager**: 8096

---

## 📊 **Operations Workflow MCP** - 智能运维工作流

### 📍 **服务信息**
- **端口**: 8090
- **服务ID**: operations_workflow_mcp
- **主要职责**: 运营工作流管理和智能介入

### 🔧 **核心功能**

#### **1. 工作流状态管理**
- 六大智能工作流监控
- 实时状态追踪
- 性能指标收集
- 异常检测和告警

#### **2. 智能介入机制**
- 自动问题检测
- 智能修复建议
- 人工介入触发
- 修复效果验证

#### **3. 自动修复功能**
- 常见问题自动修复
- 配置文件自动调整
- 服务自动重启
- 资源自动扩容

#### **4. 运营数据分析**
- 系统性能分析
- 用户行为分析
- 资源使用统计
- 趋势预测

### 🔗 **API端点**
```
GET  /api/status              - 服务状态
POST /mcp/request             - MCP请求处理
POST /api/setup_monitoring    - 设置监控
GET  /api/workflow_status     - 工作流状态
POST /api/auto_fix           - 自动修复
GET  /api/operation_logs     - 运营日志
```

### 🛠️ **管理的六大工作流**
1. **需求分析工作流** - Requirements Analysis
2. **架构设计工作流** - Architecture Design  
3. **编码实现工作流** - Coding Implementation
4. **测试验证工作流** - Test Verification
5. **部署发布工作流** - Release Deployment
6. **运维监控工作流** - Operations Monitoring

---

## 🔄 **三个MCP服务的协作关系**

### 📈 **完整DevOps流水线**
```
开发代码 → Test Manager MCP → Release Manager MCP → Operations Workflow MCP
   ↓              ↓                    ↓                      ↓
 代码提交      自动测试            自动部署              运维监控
   ↓              ↓                    ↓                      ↓
 质量检查      测试报告            部署验证              性能分析
   ↓              ↓                    ↓                      ↓
 合并请求      错误修复            健康检查              智能介入
```

### 🔗 **服务间通信**
- **统一协调**: 通过MCP Coordinator (8089) 协调
- **数据流转**: JSON格式的标准化数据交换
- **状态同步**: 实时状态更新和事件通知
- **错误处理**: 跨服务的错误传播和处理

### 🎯 **集成优势**
1. **端到端自动化** - 从代码到生产的完整自动化
2. **智能决策** - AI驱动的智能判断和处理
3. **快速反馈** - 实时状态反馈和问题定位
4. **持续改进** - 基于数据的持续优化

---

## 🌐 **服务访问地址**

### 🔗 **直接访问**
- **Test Manager MCP**: http://98.81.255.168:8097
- **Release Manager MCP**: http://98.81.255.168:8096
- **Operations Workflow MCP**: http://98.81.255.168:8090

### 🔗 **通过主API访问**
- **统一入口**: http://98.81.255.168:5001
- **工作流状态**: http://98.81.255.168:5001/api/workflows/status
- **DevOps流水线**: http://98.81.255.168:5001/api/devops/full-pipeline

---

## 🎉 **总结**

这三个专业MCP服务构成了PowerAutomation的核心DevOps能力：

1. **Test Manager MCP** 负责智能测试管理
2. **Release Manager MCP** 负责智能部署管理  
3. **Operations Workflow MCP** 负责智能运维管理

它们协同工作，提供从代码开发到生产运维的完整自动化解决方案，实现真正的AI驱动DevOps流水线。

