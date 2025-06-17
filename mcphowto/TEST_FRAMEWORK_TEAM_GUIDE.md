# PowerAutomation 测试框架团队使用指南

## 概述

PowerAutomation统一测试框架是一个企业级的测试基础设施，旨在为团队提供标准化、自动化的测试管理能力。本指南将详细介绍团队成员如何使用这个强大的测试框架来提升开发效率和代码质量。

## 快速开始

### 环境准备

团队成员首先需要确保开发环境满足以下要求：

**系统要求**
- Python 3.11+ 
- Git 2.0+
- 网络连接（用于GitHub访问）
- 至少2GB可用磁盘空间

**依赖包安装**
```bash
pip install pyyaml asyncio pathlib unittest
```

### 获取测试框架

**步骤1：克隆仓库**
```bash
git clone https://github.com/alexchuang650730/aicore0615.git
cd aicore0615/test
```

**步骤2：验证安装**
```bash
python main.py
```

如果看到测试框架的欢迎信息和状态报告，说明安装成功。

## 核心功能使用

### 测试管理器

测试管理器是整个框架的核心组件，提供统一的测试管理接口。

**查看框架状态**
```bash
python cli.py status
```

这个命令会显示：
- 测试框架版本信息
- 发现的测试模块数量
- 最近的测试执行记录
- 调度器状态
- 系统资源使用情况

**发现测试**
```bash
python cli.py discover
```

测试发现器会自动扫描项目中的所有测试文件，包括：
- 单元测试（unit_tests/）
- 集成测试（integration_tests/）
- 测试用例（testcases/）

### 测试执行

**运行comprehensive测试**
```bash
python cli.py run --type comprehensive
```

这是最常用的测试执行命令，会运行所有的comprehensive测试套件。

**并行执行**
```bash
python cli.py run --type comprehensive --workers 4
```

使用多个工作线程并行执行测试，可以显著提升执行速度。

**指定模块测试**
```bash
python cli.py run --module cloud_search_mcp
python cli.py run --module local_model_mcp
```

**测试类型选择**
```bash
python cli.py run --type unit          # 只运行单元测试
python cli.py run --type integration   # 只运行集成测试
python cli.py run --type simple        # 运行简化测试
```

### 测试报告

**生成测试报告**
```bash
python cli.py report --generate
python cli.py report --generate --type daily
python cli.py report --generate --type weekly
```

**查看报告列表**
```bash
python cli.py report --list
```

**查看特定报告**
```bash
python cli.py report --view session_20250617_123456
```

报告包含以下信息：
- 测试执行统计
- 通过/失败详情
- 性能指标
- 错误分析
- 趋势图表

### 定期调度

**启动调度器**
```bash
python cli.py schedule --start
```

**查看调度状态**
```bash
python cli.py schedule --status
```

**查看调度计划**
```bash
python cli.py schedule --list
```

**停止调度器**
```bash
python cli.py schedule --stop
```

## 配置管理

### 测试配置

测试框架的主要配置文件位于 `config/test_config.yaml`：

```yaml
# 测试发现配置
discovery:
  base_paths:
    - "../mcp/adapter"
    - "../mcp/workflow"
  include_patterns:
    - "*/unit_tests/test_*.py"
    - "*/integration_tests/test_*.py"

# 执行配置
execution:
  default_workers: 2
  timeout_seconds: 300
  retry_count: 1

# 报告配置
reporting:
  output_formats: ["json", "html"]
  include_performance: true
  include_coverage: true
```

### 调度配置

调度配置文件位于 `config/schedule_config.yaml`：

```yaml
# 调度任务配置
schedules:
  daily_comprehensive:
    cron: "0 2 * * *"  # 每天凌晨2点
    test_type: "comprehensive"
    enabled: true
    
  hourly_smoke:
    cron: "0 * * * *"  # 每小时
    test_type: "simple"
    enabled: true
    
  weekly_full:
    cron: "0 0 * * 0"  # 每周日午夜
    test_type: "all"
    enabled: true
```

## 团队协作最佳实践

### 开发工作流

**1. 功能开发前**
```bash
# 确保测试环境是最新的
git pull origin main
cd test
python cli.py discover
python cli.py run --type simple
```

**2. 开发过程中**
```bash
# 运行相关模块的测试
python cli.py run --module your_module_name
```

**3. 提交代码前**
```bash
# 运行完整测试套件
python cli.py run --type comprehensive
python cli.py report --generate
```

**4. 代码审查时**
```bash
# 查看测试报告
python cli.py report --list
python cli.py report --view latest
```

### 测试编写规范

**单元测试命名**
- 文件名：`test_{module_name}.py`
- 类名：`Test{ModuleName}`
- 方法名：`test_{function_description}`

**测试结构**
```python
class TestModuleName(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        # 测试初始化
        pass
    
    async def test_module_initialization(self):
        # 测试模块初始化
        pass
    
    async def test_core_functionality(self):
        # 测试核心功能
        pass
    
    async def asyncTearDown(self):
        # 测试清理
        pass
```

### 错误处理和调试

**查看详细错误信息**
```bash
python cli.py run --type comprehensive --verbose
```

**使用测试修复工具**
```bash
cd framework
python test_error_fixer.py
python syntax_error_fixer.py
```

**手动运行单个测试**
```bash
cd ../mcp/adapter/your_module/unit_tests
python -m unittest test_your_module.py -v
```

## 性能优化

### 并行执行优化

根据系统资源调整并行度：
- 2核CPU：`--workers 2`
- 4核CPU：`--workers 4`
- 8核CPU：`--workers 6`（留2核给系统）

### 测试选择策略

**快速验证**
```bash
python cli.py run --type simple
```

**完整验证**
```bash
python cli.py run --type comprehensive
```

**增量测试**
```bash
python cli.py run --changed-only
```

## 故障排除

### 常见问题

**问题1：测试发现失败**
```bash
# 检查路径配置
python cli.py discover --debug
```

**问题2：测试执行超时**
```bash
# 增加超时时间
python cli.py run --timeout 600
```

**问题3：并行执行冲突**
```bash
# 减少并行度
python cli.py run --workers 1
```

### 日志分析

测试框架会在 `logs/` 目录下生成详细的日志文件：
- `test_manager.log` - 管理器日志
- `test_runner.log` - 执行器日志
- `test_scheduler.log` - 调度器日志

## 高级功能

### 自定义测试套件

创建自定义测试配置：
```yaml
# custom_test_config.yaml
custom_suites:
  critical_path:
    modules: ["cloud_search_mcp", "local_model_mcp"]
    test_types: ["unit", "integration"]
    
  performance:
    modules: ["all"]
    test_types: ["performance"]
    timeout: 1800
```

### 测试数据管理

使用测试数据模板：
```python
# 在测试中使用Mock数据
from framework.test_data import MockDataManager

class TestYourModule(IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_data = MockDataManager.get_mock_data("your_module")
```

### 集成外部工具

**与IDE集成**
大多数现代IDE都支持unittest框架，可以直接在IDE中运行和调试测试。

**与代码覆盖率工具集成**
```bash
pip install coverage
coverage run --source=../mcp cli.py run --type comprehensive
coverage report
coverage html
```

## 团队培训建议

### 新成员入门

**第一周**
1. 完成环境搭建
2. 运行第一个测试
3. 理解测试框架结构
4. 学习基本命令

**第二周**
1. 编写第一个测试
2. 学习调试技巧
3. 理解报告分析
4. 参与代码审查

**第三周**
1. 掌握高级功能
2. 优化测试性能
3. 参与测试策略讨论
4. 分享最佳实践

### 持续改进

**定期回顾**
- 每月团队测试回顾会议
- 分析测试指标趋势
- 识别改进机会
- 更新最佳实践

**知识分享**
- 内部技术分享
- 测试案例研讨
- 工具使用技巧
- 问题解决经验

## 总结

PowerAutomation测试框架为团队提供了强大的测试管理能力。通过遵循本指南的最佳实践，团队成员可以：

1. **提升开发效率** - 自动化测试减少手动工作
2. **保证代码质量** - 全面的测试覆盖确保质量
3. **加强团队协作** - 统一的测试标准促进协作
4. **支持持续集成** - 为CI/CD提供坚实基础

测试框架的成功使用需要团队的共同努力和持续改进。建议团队定期回顾和优化测试流程，确保框架能够持续为项目价值创造做出贡献。

---
*文档版本: 1.0*  
*最后更新: 2025-06-17*  
*作者: Manus AI*

