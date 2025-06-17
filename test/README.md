# PowerAutomation 统一测试框架

## 概述

PowerAutomation统一测试框架是一个中央化的测试管理系统，用于管理和执行整个PowerAutomation项目的所有测试。

## 目录结构

```
test/
├── framework/              # 测试框架核心组件
│   ├── __init__.py
│   ├── test_manager.py     # 中央测试管理器
│   ├── test_scheduler.py   # 测试调度器
│   ├── test_runner.py      # 测试运行器
│   ├── test_reporter.py    # 测试报告生成器
│   └── test_discovery.py   # 测试发现器
├── config/                 # 测试配置
│   ├── test_config.yaml    # 主测试配置
│   ├── schedule_config.yaml # 调度配置
│   └── reporter_config.yaml # 报告配置
├── reports/                # 测试报告
│   ├── daily/              # 日报告
│   ├── weekly/             # 周报告
│   └── monthly/            # 月报告
├── schedules/              # 调度任务
│   ├── cron_jobs.yaml      # 定时任务配置
│   └── triggers.yaml       # 触发器配置
├── logs/                   # 测试日志
│   ├── test_execution.log  # 执行日志
│   ├── scheduler.log       # 调度日志
│   └── error.log           # 错误日志
├── main.py                 # 主入口
├── cli.py                  # 命令行接口
└── README.md               # 说明文档
```

## 核心功能

### 1. 中央化测试管理
- 统一管理所有MCP模块的测试
- 自动发现和注册测试用例
- 测试执行状态监控

### 2. 定期测试调度
- 支持cron表达式的定时测试
- 灵活的测试触发机制
- 测试任务队列管理

### 3. 智能测试报告
- 多格式报告生成（JSON、HTML、PDF）
- 测试趋势分析
- 失败测试自动分析

### 4. 测试环境管理
- 测试环境隔离
- 依赖管理
- 资源清理

## 使用方法

### 命令行使用
```bash
# 运行所有测试
python test/cli.py run --all

# 运行特定模块测试
python test/cli.py run --module cloud_search_mcp

# 启动定期测试调度
python test/cli.py schedule --start

# 生成测试报告
python test/cli.py report --type daily

# 查看测试状态
python test/cli.py status
```

### 程序化使用
```python
from test.framework import TestManager

# 创建测试管理器
manager = TestManager()

# 运行所有测试
results = await manager.run_all_tests()

# 生成报告
report = manager.generate_report(results)
```

## 配置说明

### 测试配置 (test_config.yaml)
```yaml
test_settings:
  parallel_workers: 4
  timeout: 300
  retry_count: 3
  
test_discovery:
  include_patterns:
    - "*/unit_tests/test_*.py"
    - "*/integration_tests/test_*.py"
  exclude_patterns:
    - "*/__pycache__/*"
    - "*/.*"

reporting:
  formats: ["json", "html"]
  output_dir: "reports"
  include_logs: true
```

### 调度配置 (schedule_config.yaml)
```yaml
schedules:
  daily_full_test:
    cron: "0 2 * * *"  # 每天凌晨2点
    tests: "all"
    
  hourly_smoke_test:
    cron: "0 * * * *"  # 每小时
    tests: "smoke"
    
  weekly_performance_test:
    cron: "0 3 * * 0"  # 每周日凌晨3点
    tests: "performance"
```

## 扩展功能

### 1. 测试插件系统
- 支持自定义测试插件
- 测试前后钩子函数
- 自定义报告格式

### 2. 集成支持
- CI/CD集成
- 通知系统集成
- 监控系统集成

### 3. 性能监控
- 测试执行时间监控
- 资源使用监控
- 性能趋势分析

## 最佳实践

1. **测试组织**: 按模块和功能组织测试
2. **命名规范**: 使用清晰的测试命名
3. **依赖管理**: 最小化测试间依赖
4. **资源清理**: 确保测试后资源清理
5. **报告分析**: 定期分析测试报告和趋势

## 故障排除

### 常见问题
1. **测试发现失败**: 检查路径配置和文件权限
2. **调度不工作**: 检查cron表达式和系统时间
3. **报告生成失败**: 检查输出目录权限和磁盘空间
4. **测试超时**: 调整超时配置或优化测试代码

### 日志分析
- 查看 `logs/test_execution.log` 了解测试执行详情
- 查看 `logs/scheduler.log` 了解调度问题
- 查看 `logs/error.log` 了解错误信息

## 版本历史

- v1.0.0: 初始版本，基础测试管理功能
- v1.1.0: 添加定期调度功能
- v1.2.0: 添加智能报告生成
- v1.3.0: 添加性能监控功能

## 贡献指南

1. 遵循PowerAutomation编码规范
2. 添加适当的测试用例
3. 更新相关文档
4. 提交前运行完整测试套件

