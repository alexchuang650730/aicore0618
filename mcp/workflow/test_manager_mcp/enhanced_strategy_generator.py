#!/usr/bin/env python3
"""
Enhanced Test Strategy Generator - 增强的测试策略生成器
集成到远程PowerAutomation架构中
"""

import yaml
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class TestPhase:
    """测试阶段"""
    name: str
    description: str
    duration_days: int
    parallel_level: str
    dependencies: List[str]
    deliverables: List[str]

@dataclass
class TestStrategy:
    """完整测试策略"""
    project_name: str
    project_type: str
    complexity_level: str
    test_types: List[str]
    coverage_target: float
    phases: List[TestPhase]
    risk_assessment: Dict[str, str]
    resource_requirements: Dict[str, Any]
    quality_gates: List[Dict[str, Any]]
    tools_and_frameworks: List[str]

class EnhancedTestStrategyGenerator:
    """增强的测试策略生成器，集成到远程架构"""
    
    def __init__(self):
        self.remote_integration = True
        self.strategy_templates = self._load_strategy_templates()
        
    def _load_strategy_templates(self) -> Dict[str, Any]:
<<<<<<< HEAD
        """加载测试策略模板 - 扩展更多项目类型"""
        return {
            # Web应用
            "web_app": {
                "test_types": ["unit", "integration", "e2e", "performance", "security", "accessibility"],
=======
        """加载测试策略模板"""
        return {
            "web_app": {
                "test_types": ["unit", "integration", "e2e", "performance", "security"],
>>>>>>> 0e3116c98243b7e7fddeb0eae422619dece7f4fd
                "coverage_target": 0.85,
                "phases": [
                    {"name": "单元测试", "duration": 3, "parallel": "high"},
                    {"name": "集成测试", "duration": 5, "parallel": "medium"},
                    {"name": "端到端测试", "duration": 4, "parallel": "low"},
                    {"name": "性能测试", "duration": 3, "parallel": "low"},
<<<<<<< HEAD
                    {"name": "安全测试", "duration": 2, "parallel": "low"},
                    {"name": "无障碍测试", "duration": 2, "parallel": "medium"}
                ],
                "tools": ["pytest", "selenium", "locust", "bandit", "axe-core"]
            },
            
            # API服务
=======
                    {"name": "安全测试", "duration": 2, "parallel": "low"}
                ],
                "tools": ["pytest", "selenium", "locust", "bandit"]
            },
>>>>>>> 0e3116c98243b7e7fddeb0eae422619dece7f4fd
            "api": {
                "test_types": ["unit", "integration", "contract", "performance", "security"],
                "coverage_target": 0.90,
                "phases": [
                    {"name": "单元测试", "duration": 2, "parallel": "high"},
                    {"name": "集成测试", "duration": 3, "parallel": "medium"},
                    {"name": "契约测试", "duration": 2, "parallel": "medium"},
                    {"name": "性能测试", "duration": 3, "parallel": "low"},
                    {"name": "安全测试", "duration": 2, "parallel": "low"}
                ],
                "tools": ["pytest", "postman", "pact", "jmeter", "owasp-zap"]
            },
<<<<<<< HEAD
            
            # 游戏应用
=======
>>>>>>> 0e3116c98243b7e7fddeb0eae422619dece7f4fd
            "game": {
                "test_types": ["unit", "gameplay", "performance", "ui", "compatibility"],
                "coverage_target": 0.75,
                "phases": [
                    {"name": "单元测试", "duration": 3, "parallel": "high"},
                    {"name": "游戏逻辑测试", "duration": 5, "parallel": "medium"},
                    {"name": "UI测试", "duration": 3, "parallel": "medium"},
                    {"name": "性能测试", "duration": 4, "parallel": "low"},
                    {"name": "兼容性测试", "duration": 3, "parallel": "low"}
                ],
                "tools": ["unity-test", "selenium", "unity-profiler", "device-farm"]
<<<<<<< HEAD
            },
            
            # 移动应用
            "mobile_app": {
                "test_types": ["unit", "ui", "integration", "performance", "device_compatibility", "security"],
                "coverage_target": 0.80,
                "phases": [
                    {"name": "单元测试", "duration": 3, "parallel": "high"},
                    {"name": "UI自动化测试", "duration": 4, "parallel": "medium"},
                    {"name": "集成测试", "duration": 3, "parallel": "medium"},
                    {"name": "设备兼容性测试", "duration": 5, "parallel": "low"},
                    {"name": "性能测试", "duration": 3, "parallel": "low"},
                    {"name": "安全测试", "duration": 2, "parallel": "low"}
                ],
                "tools": ["espresso", "appium", "firebase-test-lab", "charles-proxy"]
            },
            
            # 桌面应用
            "desktop_app": {
                "test_types": ["unit", "ui", "integration", "performance", "compatibility", "installation"],
                "coverage_target": 0.82,
                "phases": [
                    {"name": "单元测试", "duration": 3, "parallel": "high"},
                    {"name": "UI自动化测试", "duration": 4, "parallel": "medium"},
                    {"name": "集成测试", "duration": 3, "parallel": "medium"},
                    {"name": "兼容性测试", "duration": 4, "parallel": "low"},
                    {"name": "安装测试", "duration": 2, "parallel": "medium"},
                    {"name": "性能测试", "duration": 3, "parallel": "low"}
                ],
                "tools": ["pytest", "pyautogui", "winappdriver", "nsis-test"]
            },
            
            # 微服务架构
            "microservice": {
                "test_types": ["unit", "integration", "contract", "service_mesh", "chaos", "performance"],
                "coverage_target": 0.88,
                "phases": [
                    {"name": "单元测试", "duration": 2, "parallel": "high"},
                    {"name": "服务集成测试", "duration": 4, "parallel": "medium"},
                    {"name": "契约测试", "duration": 3, "parallel": "medium"},
                    {"name": "服务网格测试", "duration": 3, "parallel": "low"},
                    {"name": "混沌工程测试", "duration": 2, "parallel": "low"},
                    {"name": "性能测试", "duration": 4, "parallel": "low"}
                ],
                "tools": ["pytest", "pact", "istio-test", "chaos-monkey", "k6"]
            },
            
            # 数据科学/机器学习
            "ml_project": {
                "test_types": ["unit", "data_validation", "model_testing", "pipeline", "performance", "bias"],
                "coverage_target": 0.85,
                "phases": [
                    {"name": "单元测试", "duration": 2, "parallel": "high"},
                    {"name": "数据验证测试", "duration": 3, "parallel": "medium"},
                    {"name": "模型测试", "duration": 4, "parallel": "medium"},
                    {"name": "管道测试", "duration": 3, "parallel": "low"},
                    {"name": "性能测试", "duration": 3, "parallel": "low"},
                    {"name": "偏见检测测试", "duration": 2, "parallel": "medium"}
                ],
                "tools": ["pytest", "great-expectations", "mlflow", "evidently", "locust"]
            },
            
            # 区块链应用
            "blockchain": {
                "test_types": ["unit", "smart_contract", "integration", "security", "performance", "consensus"],
                "coverage_target": 0.92,
                "phases": [
                    {"name": "单元测试", "duration": 3, "parallel": "high"},
                    {"name": "智能合约测试", "duration": 5, "parallel": "medium"},
                    {"name": "集成测试", "duration": 4, "parallel": "medium"},
                    {"name": "安全审计", "duration": 4, "parallel": "low"},
                    {"name": "共识机制测试", "duration": 3, "parallel": "low"},
                    {"name": "性能测试", "duration": 3, "parallel": "low"}
                ],
                "tools": ["truffle", "hardhat", "mythril", "slither", "ganache"]
            },
            
            # IoT物联网
            "iot": {
                "test_types": ["unit", "device", "connectivity", "integration", "security", "performance"],
                "coverage_target": 0.83,
                "phases": [
                    {"name": "单元测试", "duration": 2, "parallel": "high"},
                    {"name": "设备测试", "duration": 4, "parallel": "medium"},
                    {"name": "连接性测试", "duration": 3, "parallel": "medium"},
                    {"name": "集成测试", "duration": 4, "parallel": "low"},
                    {"name": "安全测试", "duration": 3, "parallel": "low"},
                    {"name": "性能测试", "duration": 3, "parallel": "low"}
                ],
                "tools": ["pytest", "mqtt-test", "coap-test", "wireshark", "nmap"]
            },
            
            # 云原生应用
            "cloud_native": {
                "test_types": ["unit", "container", "orchestration", "scaling", "resilience", "security"],
                "coverage_target": 0.87,
                "phases": [
                    {"name": "单元测试", "duration": 2, "parallel": "high"},
                    {"name": "容器测试", "duration": 3, "parallel": "medium"},
                    {"name": "编排测试", "duration": 4, "parallel": "medium"},
                    {"name": "弹性伸缩测试", "duration": 3, "parallel": "low"},
                    {"name": "韧性测试", "duration": 3, "parallel": "low"},
                    {"name": "云安全测试", "duration": 3, "parallel": "low"}
                ],
                "tools": ["pytest", "docker-test", "kubernetes-test", "helm-test", "falco"]
=======
>>>>>>> 0e3116c98243b7e7fddeb0eae422619dece7f4fd
            }
        }
    
    async def generate_strategy_for_remote(self, project_info: Dict[str, Any]) -> Dict[str, Any]:
        """为远程架构生成测试策略"""
        try:
            project_type = project_info.get("type", "web_app")
            complexity = project_info.get("complexity", "medium")
            project_name = project_info.get("name", "Unknown Project")
            
            # 获取基础模板
            template = self.strategy_templates.get(project_type, self.strategy_templates["web_app"])
            
            # 根据复杂度调整策略
            adjusted_strategy = self._adjust_strategy_by_complexity(template, complexity)
            
            # 生成完整策略
            strategy = TestStrategy(
                project_name=project_name,
                project_type=project_type,
                complexity_level=complexity,
                test_types=adjusted_strategy["test_types"],
                coverage_target=adjusted_strategy["coverage_target"],
                phases=self._create_test_phases(adjusted_strategy["phases"]),
                risk_assessment=self._assess_risks(project_info),
                resource_requirements=self._calculate_resources(adjusted_strategy),
                quality_gates=self._define_quality_gates(adjusted_strategy),
                tools_and_frameworks=adjusted_strategy["tools"]
            )
            
            # 适配远程架构的数据格式
            return self._adapt_to_remote_format(strategy)
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "fallback_strategy": self._create_fallback_strategy(project_info)
            }
    
    def _adjust_strategy_by_complexity(self, template: Dict[str, Any], complexity: str) -> Dict[str, Any]:
        """根据复杂度调整策略"""
        adjusted = template.copy()
        
        if complexity == "simple":
            adjusted["coverage_target"] *= 0.8
            adjusted["phases"] = adjusted["phases"][:3]  # 减少测试阶段
        elif complexity == "complex":
            adjusted["coverage_target"] = min(0.95, adjusted["coverage_target"] * 1.1)
            # 增加额外的测试阶段
            adjusted["phases"].append({
                "name": "压力测试", "duration": 3, "parallel": "low"
            })
            adjusted["phases"].append({
                "name": "可靠性测试", "duration": 2, "parallel": "low"
            })
        
        return adjusted
    
    def _create_test_phases(self, phase_configs: List[Dict[str, Any]]) -> List[TestPhase]:
        """创建测试阶段对象"""
        phases = []
        for i, config in enumerate(phase_configs):
            dependencies = [phase_configs[i-1]["name"]] if i > 0 else []
            
            phase = TestPhase(
                name=config["name"],
                description=f"执行{config['name']}，确保代码质量",
                duration_days=config["duration"],
                parallel_level=config["parallel"],
                dependencies=dependencies,
                deliverables=[f"{config['name']}报告", "测试覆盖率报告"]
            )
            phases.append(phase)
        
        return phases
    
    def _assess_risks(self, project_info: Dict[str, Any]) -> Dict[str, str]:
        """评估项目风险"""
        risks = {}
        
        project_type = project_info.get("type", "web_app")
        complexity = project_info.get("complexity", "medium")
        
        if project_type == "game":
            risks["性能风险"] = "高 - 游戏性能要求严格"
            risks["兼容性风险"] = "中 - 多平台兼容性问题"
        elif project_type == "api":
            risks["安全风险"] = "高 - API安全漏洞"
            risks["性能风险"] = "中 - 高并发性能问题"
        else:
            risks["用户体验风险"] = "中 - UI/UX问题"
            risks["数据风险"] = "中 - 数据一致性问题"
        
        if complexity == "complex":
            risks["集成风险"] = "高 - 复杂系统集成问题"
            risks["维护风险"] = "中 - 代码维护复杂度高"
        
        return risks
    
    def _calculate_resources(self, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """计算资源需求"""
        total_duration = sum(phase["duration"] for phase in strategy["phases"])
        
        return {
            "测试人员": max(2, len(strategy["test_types"])),
            "测试环境": len([p for p in strategy["phases"] if p["parallel"] != "high"]),
            "预估工期": f"{total_duration}天",
            "工具许可": len(strategy["tools"]),
            "硬件需求": "标准测试环境" if total_duration < 15 else "高性能测试环境"
        }
    
    def _define_quality_gates(self, strategy: Dict[str, Any]) -> List[Dict[str, Any]]:
        """定义质量门禁"""
        gates = [
            {
                "name": "代码覆盖率",
                "threshold": strategy["coverage_target"],
                "metric": "coverage_percentage",
                "blocking": True
            },
            {
                "name": "单元测试通过率",
                "threshold": 0.95,
                "metric": "test_pass_rate",
                "blocking": True
            },
            {
                "name": "性能基准",
                "threshold": "响应时间 < 2秒",
                "metric": "response_time",
                "blocking": False
            }
        ]
        
        if "security" in strategy["test_types"]:
            gates.append({
                "name": "安全扫描",
                "threshold": "无高危漏洞",
                "metric": "security_score",
                "blocking": True
            })
        
        return gates
    
    def _adapt_to_remote_format(self, strategy: TestStrategy) -> Dict[str, Any]:
        """适配远程架构的数据格式"""
        return {
            "success": True,
            "strategy_id": f"strategy_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "project_name": strategy.project_name,
            "project_type": strategy.project_type,
            "complexity_level": strategy.complexity_level,
            "test_types": strategy.test_types,
            "coverage_target": strategy.coverage_target,
            "phases": [asdict(phase) for phase in strategy.phases],
            "risk_assessment": strategy.risk_assessment,
            "resource_requirements": strategy.resource_requirements,
            "quality_gates": strategy.quality_gates,
            "tools_and_frameworks": strategy.tools_and_frameworks,
            "generated_at": datetime.now().isoformat(),
            "generator_version": "enhanced_v1.0"
        }
    
    def _create_fallback_strategy(self, project_info: Dict[str, Any]) -> Dict[str, Any]:
        """创建后备策略"""
        return {
            "strategy_id": f"fallback_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "project_name": project_info.get("name", "Unknown"),
            "test_types": ["unit", "integration"],
            "coverage_target": 0.7,
            "phases": [
                {"name": "基础测试", "duration_days": 5, "parallel_level": "medium"}
            ],
            "tools_and_frameworks": ["pytest"],
            "note": "使用简化的后备测试策略"
        }

<<<<<<< HEAD

    def detect_project_type(self, project_info: Dict[str, Any]) -> str:
        """智能检测项目类型"""
        # 获取项目描述、技术栈、文件结构等信息
        description = project_info.get("description", "").lower()
        tech_stack = project_info.get("tech_stack", [])
        file_structure = project_info.get("files", [])
        
        # 技术栈关键词映射
        tech_keywords = {
            "mobile_app": ["react-native", "flutter", "swift", "kotlin", "xamarin", "ionic"],
            "web_app": ["react", "vue", "angular", "django", "flask", "express", "next.js"],
            "api": ["fastapi", "express", "spring", "gin", "rails", "laravel"],
            "game": ["unity", "unreal", "godot", "pygame", "phaser"],
            "desktop_app": ["electron", "tkinter", "qt", "wpf", "javafx"],
            "microservice": ["docker", "kubernetes", "istio", "consul", "eureka"],
            "ml_project": ["tensorflow", "pytorch", "scikit-learn", "pandas", "jupyter"],
            "blockchain": ["solidity", "web3", "truffle", "hardhat", "ethereum"],
            "iot": ["arduino", "raspberry-pi", "mqtt", "coap", "zigbee"],
            "cloud_native": ["kubernetes", "helm", "terraform", "aws", "gcp", "azure"]
        }
        
        # 文件扩展名映射
        file_extensions = {
            "mobile_app": [".swift", ".kt", ".dart", ".xaml"],
            "web_app": [".html", ".css", ".js", ".jsx", ".vue", ".tsx"],
            "game": [".cs", ".cpp", ".gd", ".lua"],
            "blockchain": [".sol", ".vy"],
            "ml_project": [".ipynb", ".py", ".r"],
            "iot": [".ino", ".c", ".h"]
        }
        
        # 描述关键词映射
        description_keywords = {
            "mobile_app": ["mobile", "app", "ios", "android", "smartphone"],
            "web_app": ["website", "web", "frontend", "backend", "browser"],
            "api": ["api", "rest", "graphql", "microservice", "endpoint"],
            "game": ["game", "gaming", "3d", "2d", "player", "level"],
            "desktop_app": ["desktop", "application", "gui", "window"],
            "microservice": ["microservice", "distributed", "service mesh"],
            "ml_project": ["machine learning", "ai", "model", "prediction", "data science"],
            "blockchain": ["blockchain", "smart contract", "defi", "nft", "crypto"],
            "iot": ["iot", "sensor", "device", "embedded", "hardware"],
            "cloud_native": ["cloud", "container", "serverless", "kubernetes"]
        }
        
        # 计算每种项目类型的匹配分数
        scores = {}
        for project_type in self.strategy_templates.keys():
            score = 0
            
            # 技术栈匹配
            if project_type in tech_keywords:
                for tech in tech_stack:
                    if any(keyword in tech.lower() for keyword in tech_keywords[project_type]):
                        score += 3
            
            # 文件扩展名匹配
            if project_type in file_extensions:
                for file_path in file_structure:
                    if any(file_path.endswith(ext) for ext in file_extensions[project_type]):
                        score += 2
            
            # 描述关键词匹配
            if project_type in description_keywords:
                for keyword in description_keywords[project_type]:
                    if keyword in description:
                        score += 1
            
            scores[project_type] = score
        
        # 返回得分最高的项目类型
        if scores:
            best_match = max(scores, key=scores.get)
            if scores[best_match] > 0:
                return best_match
        
        # 默认返回web_app
        return "web_app"
    
    def get_supported_project_types(self) -> List[str]:
        """获取支持的项目类型列表"""
        return list(self.strategy_templates.keys())
    
    def get_project_type_info(self, project_type: str) -> Dict[str, Any]:
        """获取项目类型的详细信息"""
        if project_type in self.strategy_templates:
            template = self.strategy_templates[project_type]
            return {
                "type": project_type,
                "test_types": template["test_types"],
                "coverage_target": template["coverage_target"],
                "phase_count": len(template["phases"]),
                "estimated_duration": sum(phase["duration"] for phase in template["phases"]),
                "tools": template["tools"],
                "description": self._get_project_type_description(project_type)
            }
        return {}
    
    def _get_project_type_description(self, project_type: str) -> str:
        """获取项目类型的描述"""
        descriptions = {
            "web_app": "Web应用程序，包括前端和后端开发",
            "api": "API服务，专注于接口开发和集成",
            "game": "游戏应用，包括2D/3D游戏开发",
            "mobile_app": "移动应用，支持iOS和Android平台",
            "desktop_app": "桌面应用程序，跨平台GUI应用",
            "microservice": "微服务架构，分布式系统开发",
            "ml_project": "机器学习项目，AI模型开发和部署",
            "blockchain": "区块链应用，智能合约和DApp开发",
            "iot": "物联网项目，嵌入式设备和传感器",
            "cloud_native": "云原生应用，容器化和Kubernetes部署"
        }
        return descriptions.get(project_type, "未知项目类型")

=======
>>>>>>> 0e3116c98243b7e7fddeb0eae422619dece7f4fd
