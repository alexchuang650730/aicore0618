#!/usr/bin/env python3
"""
Enhanced Test Case Generator - 增强的测试用例生成器
集成到远程PowerAutomation架构中
"""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class TestCase:
    """测试用例"""
    id: str
    name: str
    description: str
    category: str
    priority: str
    test_type: str
    preconditions: List[str]
    steps: List[str]
    expected_result: str
    test_data: Dict[str, Any]
    automation_level: str

class EnhancedTestCaseGenerator:
    """增强的测试用例生成器"""
    
    def __init__(self):
        self.remote_integration = True
        self.case_templates = self._load_case_templates()
        
    def _load_case_templates(self) -> Dict[str, Any]:
<<<<<<< HEAD
        """加载测试用例模板 - 优化准确性"""
        return {
            "unit": {
                "categories": ["功能测试", "边界值测试", "异常测试", "状态测试", "数据验证"],
                "priorities": ["高", "中", "低"],
                "automation_level": "完全自动化",
                "patterns": {
                    "功能测试": ["正常输入验证", "返回值检查", "方法调用验证"],
                    "边界值测试": ["最小值测试", "最大值测试", "临界值测试"],
                    "异常测试": ["空值处理", "无效输入", "异常抛出验证"],
                    "状态测试": ["对象状态变化", "状态转换验证", "状态一致性"],
                    "数据验证": ["数据类型检查", "数据格式验证", "数据完整性"]
                }
            },
            "integration": {
                "categories": ["接口测试", "数据流测试", "系统集成测试", "服务交互测试", "依赖测试"],
                "priorities": ["高", "中"],
                "automation_level": "部分自动化",
                "patterns": {
                    "接口测试": ["API调用验证", "参数传递测试", "响应格式检查"],
                    "数据流测试": ["数据传输验证", "数据转换测试", "数据一致性"],
                    "系统集成测试": ["模块间交互", "系统间通信", "集成点验证"],
                    "服务交互测试": ["服务调用链", "服务依赖验证", "服务降级测试"],
                    "依赖测试": ["外部依赖验证", "依赖失败处理", "依赖版本兼容"]
                }
            },
            "e2e": {
                "categories": ["用户场景测试", "业务流程测试", "端到端测试", "用户体验测试", "跨平台测试"],
                "priorities": ["高", "中"],
                "automation_level": "部分自动化",
                "patterns": {
                    "用户场景测试": ["典型用户路径", "用户操作序列", "用户目标达成"],
                    "业务流程测试": ["完整业务流程", "业务规则验证", "流程异常处理"],
                    "端到端测试": ["系统完整链路", "数据端到端流转", "功能完整性"],
                    "用户体验测试": ["界面响应性", "操作便利性", "错误提示友好性"],
                    "跨平台测试": ["多浏览器兼容", "多设备适配", "多操作系统支持"]
                }
            },
            "performance": {
                "categories": ["负载测试", "压力测试", "容量测试", "稳定性测试", "资源使用测试"],
                "priorities": ["中", "低"],
                "automation_level": "完全自动化",
                "patterns": {
                    "负载测试": ["正常负载验证", "峰值负载测试", "负载分布测试"],
                    "压力测试": ["极限压力测试", "压力恢复测试", "压力点识别"],
                    "容量测试": ["最大容量验证", "容量扩展测试", "容量限制测试"],
                    "稳定性测试": ["长时间运行", "内存泄漏检测", "系统稳定性"],
                    "资源使用测试": ["CPU使用率", "内存使用量", "磁盘I/O性能"]
                }
            },
            "security": {
                "categories": ["认证测试", "授权测试", "数据安全测试", "输入验证测试", "会话管理测试"],
                "priorities": ["高"],
                "automation_level": "部分自动化",
                "patterns": {
                    "认证测试": ["登录验证", "密码策略", "多因素认证"],
                    "授权测试": ["权限控制", "角色验证", "访问控制"],
                    "数据安全测试": ["数据加密", "敏感数据保护", "数据传输安全"],
                    "输入验证测试": ["SQL注入防护", "XSS防护", "输入过滤"],
                    "会话管理测试": ["会话超时", "会话固定", "会话劫持防护"]
                }
            },
            # 新增测试类型
            "accessibility": {
                "categories": ["键盘导航测试", "屏幕阅读器测试", "色彩对比测试", "语义标记测试"],
                "priorities": ["中"],
                "automation_level": "部分自动化",
                "patterns": {
                    "键盘导航测试": ["Tab键导航", "快捷键功能", "焦点管理"],
                    "屏幕阅读器测试": ["语音输出验证", "标签读取", "内容结构"],
                    "色彩对比测试": ["对比度检查", "色盲友好", "高对比模式"],
                    "语义标记测试": ["HTML语义", "ARIA标签", "标题结构"]
                }
            },
            "ui": {
                "categories": ["界面布局测试", "交互测试", "响应式测试", "视觉回归测试"],
                "priorities": ["中", "低"],
                "automation_level": "部分自动化",
                "patterns": {
                    "界面布局测试": ["元素位置", "布局适配", "内容显示"],
                    "交互测试": ["点击响应", "拖拽功能", "手势操作"],
                    "响应式测试": ["屏幕适配", "分辨率测试", "设备兼容"],
                    "视觉回归测试": ["界面截图对比", "样式变化检测", "视觉一致性"]
                }
            },
            "compatibility": {
                "categories": ["浏览器兼容测试", "操作系统兼容测试", "设备兼容测试", "版本兼容测试"],
                "priorities": ["中"],
                "automation_level": "部分自动化",
                "patterns": {
                    "浏览器兼容测试": ["Chrome兼容", "Firefox兼容", "Safari兼容", "Edge兼容"],
                    "操作系统兼容测试": ["Windows兼容", "macOS兼容", "Linux兼容"],
                    "设备兼容测试": ["移动设备", "平板设备", "桌面设备"],
                    "版本兼容测试": ["向前兼容", "向后兼容", "版本升级测试"]
                }
=======
        """加载测试用例模板"""
        return {
            "unit": {
                "categories": ["功能测试", "边界值测试", "异常测试"],
                "priorities": ["高", "中", "低"],
                "automation_level": "完全自动化"
            },
            "integration": {
                "categories": ["接口测试", "数据流测试", "系统集成测试"],
                "priorities": ["高", "中"],
                "automation_level": "部分自动化"
            },
            "e2e": {
                "categories": ["用户场景测试", "业务流程测试", "端到端测试"],
                "priorities": ["高", "中"],
                "automation_level": "部分自动化"
            },
            "performance": {
                "categories": ["负载测试", "压力测试", "容量测试"],
                "priorities": ["中", "低"],
                "automation_level": "完全自动化"
            },
            "security": {
                "categories": ["认证测试", "授权测试", "数据安全测试"],
                "priorities": ["高"],
                "automation_level": "部分自动化"
>>>>>>> 0e3116c98243b7e7fddeb0eae422619dece7f4fd
            }
        }
    
    async def generate_cases_for_remote(self, strategy: Dict[str, Any], requirements: Dict[str, Any] = None) -> Dict[str, Any]:
        """为远程架构生成测试用例"""
        try:
            test_types = strategy.get("test_types", ["unit", "integration"])
            project_type = strategy.get("project_type", "web_app")
            project_name = strategy.get("project_name", "Unknown Project")
            
            all_test_cases = []
            case_summary = {}
            
            # 为每种测试类型生成用例
            for test_type in test_types:
                cases = self._generate_cases_by_type(test_type, project_type, requirements)
                all_test_cases.extend(cases)
                case_summary[test_type] = len(cases)
            
            # 生成特殊场景用例
            special_cases = self._generate_special_scenario_cases(project_type, requirements)
            all_test_cases.extend(special_cases)
            case_summary["special_scenarios"] = len(special_cases)
            
            return self._format_for_remote({
                "project_name": project_name,
                "total_cases": len(all_test_cases),
                "case_summary": case_summary,
                "test_cases": all_test_cases,
                "automation_rate": self._calculate_automation_rate(all_test_cases),
                "estimated_execution_time": self._estimate_execution_time(all_test_cases)
            })
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "fallback_cases": self._create_fallback_cases(strategy)
            }
    
    def _generate_cases_by_type(self, test_type: str, project_type: str, requirements: Dict[str, Any] = None) -> List[TestCase]:
        """根据测试类型生成用例"""
        template = self.case_templates.get(test_type, self.case_templates["unit"])
        cases = []
        
        for i, category in enumerate(template["categories"]):
            # 为每个类别生成多个用例
            case_count = 3 if test_type == "unit" else 2
            
            for j in range(case_count):
                case_id = f"{test_type}_{category.replace(' ', '_')}_{i+1}_{j+1}"
                
                case = TestCase(
                    id=case_id,
                    name=f"{category} - 场景 {j+1}",
                    description=self._generate_case_description(test_type, category, project_type),
                    category=category,
                    priority=template["priorities"][min(j, len(template["priorities"])-1)],
                    test_type=test_type,
                    preconditions=self._generate_preconditions(test_type, project_type),
                    steps=self._generate_test_steps(test_type, category, project_type),
                    expected_result=self._generate_expected_result(test_type, category),
                    test_data=self._generate_test_data(test_type, category, project_type),
                    automation_level=template["automation_level"]
                )
                
                cases.append(case)
        
        return cases
    
    def _generate_case_description(self, test_type: str, category: str, project_type: str) -> str:
        """生成用例描述"""
        descriptions = {
            "unit": {
                "功能测试": f"验证{project_type}核心功能模块的正确性",
                "边界值测试": f"测试{project_type}输入参数的边界值处理",
                "异常测试": f"验证{project_type}异常情况的处理机制"
            },
            "integration": {
                "接口测试": f"验证{project_type}各模块间接口的正确性",
                "数据流测试": f"测试{project_type}数据在系统中的流转",
                "系统集成测试": f"验证{project_type}与外部系统的集成"
            },
            "e2e": {
                "用户场景测试": f"模拟真实用户使用{project_type}的完整场景",
                "业务流程测试": f"验证{project_type}核心业务流程的完整性",
                "端到端测试": f"测试{project_type}从前端到后端的完整链路"
            }
        }
        
        return descriptions.get(test_type, {}).get(category, f"测试{category}的功能")
    
    def _generate_preconditions(self, test_type: str, project_type: str) -> List[str]:
        """生成前置条件"""
        base_conditions = {
            "unit": ["测试环境已搭建", "依赖模块已mock"],
            "integration": ["测试环境已搭建", "相关服务已启动", "测试数据已准备"],
            "e2e": ["完整测试环境已搭建", "用户账号已创建", "测试数据已初始化"],
            "performance": ["性能测试环境已搭建", "监控工具已配置", "基准数据已收集"],
            "security": ["安全测试环境已搭建", "测试账号已配置", "安全工具已准备"]
        }
        
        conditions = base_conditions.get(test_type, ["测试环境已准备"])
        
        # 根据项目类型添加特定条件
        if project_type == "game":
            conditions.append("游戏引擎已启动")
        elif project_type == "api":
            conditions.append("API服务已启动")
        elif project_type == "web_app":
            conditions.append("Web服务器已启动")
        
        return conditions
    
    def _generate_test_steps(self, test_type: str, category: str, project_type: str) -> List[str]:
        """生成测试步骤"""
        if test_type == "unit":
            return [
                "1. 准备测试数据",
                "2. 调用被测试方法",
                "3. 验证返回结果",
                "4. 检查副作用"
            ]
        elif test_type == "integration":
            return [
                "1. 启动相关服务",
                "2. 发送测试请求",
                "3. 验证响应数据",
                "4. 检查数据一致性",
                "5. 清理测试数据"
            ]
        elif test_type == "e2e":
            if project_type == "web_app":
                return [
                    "1. 打开浏览器访问应用",
                    "2. 执行用户操作流程",
                    "3. 验证页面响应",
                    "4. 检查数据更新",
                    "5. 关闭浏览器"
                ]
            elif project_type == "game":
                return [
                    "1. 启动游戏客户端",
                    "2. 执行游戏操作",
                    "3. 验证游戏状态",
                    "4. 检查游戏数据",
                    "5. 退出游戏"
                ]
        
        return ["1. 执行测试操作", "2. 验证测试结果"]
    
    def _generate_expected_result(self, test_type: str, category: str) -> str:
        """生成期望结果"""
        results = {
            "功能测试": "功能按预期正常工作，返回正确结果",
            "边界值测试": "边界值处理正确，无异常抛出",
            "异常测试": "异常情况得到正确处理，返回合适的错误信息",
            "接口测试": "接口响应正确，数据格式符合规范",
            "数据流测试": "数据正确传递，无数据丢失或损坏",
            "用户场景测试": "用户操作流程顺畅，达到预期目标",
            "负载测试": "系统在预期负载下稳定运行",
            "安全测试": "系统安全机制有效，无安全漏洞"
        }
        
        return results.get(category, "测试通过，系统行为符合预期")
    
    def _generate_test_data(self, test_type: str, category: str, project_type: str) -> Dict[str, Any]:
        """生成测试数据"""
        base_data = {
            "test_id": f"{test_type}_{category}",
            "timestamp": datetime.now().isoformat()
        }
        
        if test_type == "unit":
            base_data.update({
                "input_params": {"param1": "value1", "param2": "value2"},
                "mock_data": {"service_response": "success"}
            })
        elif test_type == "integration":
            base_data.update({
                "api_endpoint": "/api/test",
                "request_data": {"key": "value"},
                "expected_status": 200
            })
        elif test_type == "e2e":
            if project_type == "web_app":
                base_data.update({
                    "user_credentials": {"username": "testuser", "password": "testpass"},
                    "test_url": "http://localhost:3000",
                    "browser": "chrome"
                })
        
        return base_data
    
    def _generate_special_scenario_cases(self, project_type: str, requirements: Dict[str, Any] = None) -> List[TestCase]:
        """生成特殊场景用例"""
        special_cases = []
        
        # 错误处理场景
        error_case = TestCase(
            id="special_error_handling_001",
            name="系统错误处理验证",
            description="验证系统在各种错误情况下的处理能力",
            category="错误处理",
            priority="高",
            test_type="integration",
            preconditions=["系统正常运行"],
            steps=[
                "1. 模拟网络中断",
                "2. 模拟数据库连接失败",
                "3. 模拟内存不足",
                "4. 验证错误处理机制"
            ],
            expected_result="系统优雅处理各种错误，提供合适的用户反馈",
            test_data={"error_types": ["network", "database", "memory"]},
            automation_level="部分自动化"
        )
        special_cases.append(error_case)
        
        # 并发场景
        if project_type in ["web_app", "api"]:
            concurrent_case = TestCase(
                id="special_concurrent_001",
                name="并发访问测试",
                description="验证系统在高并发情况下的稳定性",
                category="并发测试",
                priority="中",
                test_type="performance",
                preconditions=["性能测试环境已准备"],
                steps=[
                    "1. 配置并发用户数",
                    "2. 同时发起多个请求",
                    "3. 监控系统响应",
                    "4. 分析性能指标"
                ],
                expected_result="系统在并发访问下保持稳定，响应时间在可接受范围内",
                test_data={"concurrent_users": 100, "duration": "5min"},
                automation_level="完全自动化"
            )
            special_cases.append(concurrent_case)
        
        return special_cases
    
    def _calculate_automation_rate(self, test_cases: List[TestCase]) -> float:
        """计算自动化率"""
        if not test_cases:
            return 0.0
        
        automated_count = sum(1 for case in test_cases 
                            if case.automation_level in ["完全自动化", "部分自动化"])
        return round(automated_count / len(test_cases), 2)
    
    def _estimate_execution_time(self, test_cases: List[TestCase]) -> Dict[str, Any]:
        """估算执行时间"""
        time_mapping = {
            "unit": 2,  # 分钟
            "integration": 5,
            "e2e": 10,
            "performance": 30,
            "security": 15
        }
        
        total_minutes = sum(time_mapping.get(case.test_type, 5) for case in test_cases)
        
        return {
            "total_minutes": total_minutes,
            "total_hours": round(total_minutes / 60, 1),
            "estimated_days": max(1, round(total_minutes / (8 * 60), 1)),
            "parallel_execution_hours": round(total_minutes / 4 / 60, 1)  # 假设4个并行执行
        }
    
    def _format_for_remote(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """格式化为远程架构格式"""
        # 转换TestCase对象为字典
        if "test_cases" in data:
            data["test_cases"] = [asdict(case) for case in data["test_cases"]]
        
        return {
            "success": True,
            "generation_id": f"cases_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "generated_at": datetime.now().isoformat(),
            "generator_version": "enhanced_v1.0",
            **data
        }
    
    def _create_fallback_cases(self, strategy: Dict[str, Any]) -> List[Dict[str, Any]]:
        """创建后备用例"""
        return [
            {
                "id": "fallback_001",
                "name": "基础功能测试",
                "description": "验证系统基础功能",
                "category": "功能测试",
                "priority": "高",
                "test_type": "unit",
                "automation_level": "完全自动化"
            }
        ]

<<<<<<< HEAD

    def _generate_cases_by_type(self, test_type: str, project_type: str, requirements: Dict[str, Any] = None) -> List[TestCase]:
        """根据测试类型生成精确的测试用例"""
        if test_type not in self.case_templates:
            return []
        
        template = self.case_templates[test_type]
        cases = []
        
        # 基于项目类型调整用例生成策略
        project_specific_adjustments = self._get_project_specific_adjustments(project_type, test_type)
        
        # 为每个类别生成用例
        for category in template["categories"]:
            patterns = template["patterns"].get(category, [])
            
            for pattern in patterns:
                case = self._create_detailed_test_case(
                    test_type=test_type,
                    category=category,
                    pattern=pattern,
                    project_type=project_type,
                    requirements=requirements,
                    adjustments=project_specific_adjustments
                )
                cases.append(case)
        
        return cases
    
    def _get_project_specific_adjustments(self, project_type: str, test_type: str) -> Dict[str, Any]:
        """获取项目类型特定的调整"""
        adjustments = {
            "mobile_app": {
                "ui": {"focus": "触摸交互", "platforms": ["iOS", "Android"]},
                "performance": {"metrics": ["启动时间", "内存使用", "电池消耗"]},
                "compatibility": {"devices": ["手机", "平板"], "os_versions": ["多版本"]}
            },
            "web_app": {
                "ui": {"focus": "响应式设计", "browsers": ["Chrome", "Firefox", "Safari"]},
                "performance": {"metrics": ["页面加载时间", "首屏渲染", "交互响应"]},
                "accessibility": {"standards": ["WCAG 2.1", "Section 508"]}
            },
            "api": {
                "integration": {"focus": "接口契约", "protocols": ["REST", "GraphQL"]},
                "performance": {"metrics": ["响应时间", "吞吐量", "并发处理"]},
                "security": {"focus": ["认证", "授权", "数据验证"]}
            },
            "microservice": {
                "integration": {"focus": "服务间通信", "patterns": ["同步", "异步"]},
                "performance": {"metrics": ["服务延迟", "链路追踪", "熔断恢复"]},
                "security": {"focus": ["服务认证", "网络安全", "数据加密"]}
            },
            "blockchain": {
                "security": {"focus": ["智能合约安全", "交易验证", "共识机制"]},
                "performance": {"metrics": ["交易吞吐量", "确认时间", "Gas消耗"]},
                "integration": {"focus": ["链上链下交互", "跨链通信"]}
            },
            "ml_project": {
                "data_validation": {"focus": ["数据质量", "特征工程", "模型验证"]},
                "performance": {"metrics": ["推理速度", "模型精度", "资源消耗"]},
                "bias": {"focus": ["公平性检测", "偏见识别", "模型解释性"]}
            }
        }
        
        return adjustments.get(project_type, {}).get(test_type, {})
    
    def _create_detailed_test_case(self, test_type: str, category: str, pattern: str, 
                                 project_type: str, requirements: Dict[str, Any] = None,
                                 adjustments: Dict[str, Any] = None) -> TestCase:
        """创建详细的测试用例"""
        case_id = f"{test_type}_{category}_{pattern}".replace(" ", "_").replace("测试", "").lower()
        
        # 基于模式生成具体的测试步骤
        steps = self._generate_test_steps(test_type, category, pattern, project_type, adjustments)
        
        # 生成测试数据
        test_data = self._generate_test_data(test_type, category, pattern, project_type, requirements)
        
        # 生成期望结果
        expected_result = self._generate_expected_result(test_type, category, pattern, adjustments)
        
        # 生成前置条件
        preconditions = self._generate_preconditions(test_type, category, project_type)
        
        # 确定优先级
        priority = self._determine_priority(test_type, category, pattern, project_type)
        
        return TestCase(
            id=case_id,
            name=f"{category} - {pattern}",
            description=f"验证{pattern}在{project_type}项目中的{category}功能",
            category=category,
            priority=priority,
            test_type=test_type,
            preconditions=preconditions,
            steps=steps,
            expected_result=expected_result,
            test_data=test_data,
            automation_level=self.case_templates[test_type]["automation_level"]
        )
    
    def _generate_test_steps(self, test_type: str, category: str, pattern: str, 
                           project_type: str, adjustments: Dict[str, Any] = None) -> List[str]:
        """生成详细的测试步骤"""
        base_steps = {
            "unit": [
                "1. 准备测试环境和测试数据",
                "2. 初始化被测试的类或方法",
                "3. 执行测试方法并传入测试参数",
                "4. 验证返回结果是否符合预期",
                "5. 清理测试环境和资源"
            ],
            "integration": [
                "1. 启动相关的系统组件和服务",
                "2. 配置组件间的连接和依赖关系",
                "3. 发送测试请求到目标接口",
                "4. 验证数据在组件间的正确传递",
                "5. 检查系统状态和日志信息",
                "6. 关闭测试环境"
            ],
            "e2e": [
                "1. 启动完整的应用程序环境",
                "2. 模拟真实用户的操作流程",
                "3. 执行完整的业务场景操作",
                "4. 验证每个步骤的界面反馈",
                "5. 检查最终的业务结果",
                "6. 验证数据的完整性和一致性"
            ],
            "performance": [
                "1. 配置性能测试环境和监控工具",
                "2. 设置测试负载和并发用户数",
                "3. 执行性能测试场景",
                "4. 监控系统资源使用情况",
                "5. 收集性能指标数据",
                "6. 分析性能瓶颈和优化建议"
            ],
            "security": [
                "1. 配置安全测试环境",
                "2. 准备安全测试工具和脚本",
                "3. 执行安全漏洞扫描",
                "4. 尝试各种攻击场景",
                "5. 验证安全防护机制",
                "6. 生成安全测试报告"
            ]
        }
        
        steps = base_steps.get(test_type, ["1. 执行测试", "2. 验证结果"])
        
        # 根据项目类型和调整信息定制步骤
        if adjustments and project_type == "mobile_app" and test_type == "ui":
            steps.insert(2, "2.1. 测试触摸手势和多点触控")
            steps.insert(3, "2.2. 验证不同屏幕尺寸的适配")
        
        return steps
    
    def _generate_test_data(self, test_type: str, category: str, pattern: str, 
                          project_type: str, requirements: Dict[str, Any] = None) -> Dict[str, Any]:
        """生成测试数据"""
        base_data = {
            "test_environment": "测试环境",
            "test_user": "test_user",
            "test_timestamp": datetime.now().isoformat()
        }
        
        # 根据测试类型添加特定数据
        if test_type == "unit":
            base_data.update({
                "input_values": ["正常值", "边界值", "异常值"],
                "expected_outputs": ["预期结果1", "预期结果2", "异常处理"]
            })
        elif test_type == "performance":
            base_data.update({
                "concurrent_users": 100,
                "test_duration": "10分钟",
                "performance_thresholds": {
                    "response_time": "< 2秒",
                    "throughput": "> 1000 TPS",
                    "error_rate": "< 1%"
                }
            })
        elif test_type == "security":
            base_data.update({
                "attack_vectors": ["SQL注入", "XSS攻击", "CSRF攻击"],
                "security_tools": ["OWASP ZAP", "Burp Suite"],
                "compliance_standards": ["OWASP Top 10", "ISO 27001"]
            })
        
        # 根据项目类型调整数据
        if project_type == "mobile_app":
            base_data["test_devices"] = ["iPhone 12", "Samsung Galaxy S21", "iPad Pro"]
        elif project_type == "web_app":
            base_data["test_browsers"] = ["Chrome 91+", "Firefox 89+", "Safari 14+"]
        
        return base_data
    
    def _generate_expected_result(self, test_type: str, category: str, pattern: str, 
                                adjustments: Dict[str, Any] = None) -> str:
        """生成期望结果"""
        result_templates = {
            "unit": f"{pattern}执行成功，返回预期结果，无异常抛出",
            "integration": f"组件间{pattern}正常，数据传递准确，系统状态正确",
            "e2e": f"用户{pattern}流程完整，界面响应正确，业务目标达成",
            "performance": f"系统在{pattern}场景下性能指标满足要求",
            "security": f"系统在{pattern}测试中安全防护有效，无安全漏洞"
        }
        
        base_result = result_templates.get(test_type, f"{pattern}测试通过")
        
        # 根据调整信息添加特定期望
        if adjustments:
            if "metrics" in adjustments:
                metrics = ", ".join(adjustments["metrics"])
                base_result += f"，{metrics}指标正常"
        
        return base_result
    
    def _generate_preconditions(self, test_type: str, category: str, project_type: str) -> List[str]:
        """生成前置条件"""
        base_conditions = [
            "测试环境已准备就绪",
            "测试数据已准备完毕",
            "相关权限已配置"
        ]
        
        # 根据测试类型添加特定条件
        type_conditions = {
            "unit": ["开发环境已搭建", "单元测试框架已配置"],
            "integration": ["所有相关服务已启动", "网络连接正常"],
            "e2e": ["完整应用环境已部署", "测试用户账号已创建"],
            "performance": ["性能测试工具已安装", "监控系统已配置"],
            "security": ["安全测试工具已准备", "测试权限已申请"]
        }
        
        base_conditions.extend(type_conditions.get(test_type, []))
        
        # 根据项目类型添加特定条件
        if project_type == "mobile_app":
            base_conditions.append("测试设备已连接并配置")
        elif project_type == "web_app":
            base_conditions.append("测试浏览器已安装并配置")
        
        return base_conditions
    
    def _determine_priority(self, test_type: str, category: str, pattern: str, project_type: str) -> str:
        """确定测试优先级"""
        # 高优先级模式
        high_priority_patterns = [
            "正常输入验证", "API调用验证", "典型用户路径", "登录验证", "数据加密"
        ]
        
        # 中优先级模式
        medium_priority_patterns = [
            "边界值测试", "数据传输验证", "界面响应性", "负载测试"
        ]
        
        if pattern in high_priority_patterns:
            return "高"
        elif pattern in medium_priority_patterns:
            return "中"
        else:
            return "低"

=======
>>>>>>> 0e3116c98243b7e7fddeb0eae422619dece7f4fd
