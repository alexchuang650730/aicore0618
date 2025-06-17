#!/usr/bin/env python3
"""
基础工作流类
Base Workflow Class

为PowerAuto架构提供标准化的工作流基础类
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
import toml
import yaml
import json
import logging
from pathlib import Path

class BaseWorkflow(ABC):
    """工作流基础类"""
    
    def __init__(self, config_dir: str):
        self.config_dir = config_dir
        self.config = self._load_config()
        self.routing_rules = self._load_routing_rules()
        self.processing_steps = self._load_processing_steps()
        self.quality_settings = self._load_quality_settings()
        
        # 初始化adapter
        self.adapters = self._initialize_adapters()
        
        # 设置日志
        self.logger = self._setup_logging()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载主配置文件"""
        config_path = f"{self.config_dir}/workflow_config.toml"
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return toml.load(f)
        except FileNotFoundError:
            return {"workflow": {"name": "Unknown", "version": "1.0.0"}}
    
    def _load_routing_rules(self) -> Dict[str, Any]:
        """加载路由规则"""
        rules_path = f"{self.config_dir}/routing_rules.yaml"
        try:
            with open(rules_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            return {"routing_rules": {}}
    
    def _load_processing_steps(self) -> Dict[str, Any]:
        """加载处理步骤"""
        steps_path = f"{self.config_dir}/processing_steps.json"
        try:
            with open(steps_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"steps": []}
    
    def _load_quality_settings(self) -> Dict[str, Any]:
        """加载质量设置"""
        quality_path = f"{self.config_dir}/quality_settings.toml"
        try:
            with open(quality_path, 'r', encoding='utf-8') as f:
                return toml.load(f)
        except FileNotFoundError:
            return {"quality": {"min_confidence": 0.7}}
    
    @abstractmethod
    def _initialize_adapters(self) -> Dict[str, Any]:
        """初始化所需的adapter"""
        pass
    
    def _setup_logging(self) -> logging.Logger:
        """设置日志"""
        logger = logging.getLogger(self.config.get('workflow', {}).get('name', 'BaseWorkflow'))
        logger.setLevel(logging.INFO)
        
        # 创建控制台处理器
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    def select_adapter(self, request: Dict[str, Any]) -> str:
        """根据路由规则选择adapter"""
        # 默认选择本地模型
        return "local_model_mcp"
    
    def execute_step(self, step_config: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """执行单个处理步骤"""
        # 默认实现
        return {"status": "completed", "step": step_config.get("id", "unknown")}
    
    def execute(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """执行完整工作流"""
        context = {"request": request, "results": {}}
        
        try:
            for step in self.processing_steps.get('steps', []):
                if self._should_execute_step(step, context):
                    result = self.execute_step(step, context)
                    context['results'][step['id']] = result
            
            return self._format_final_result(context)
            
        except Exception as e:
            self.logger.error(f"工作流执行失败: {e}")
            return self._handle_workflow_error(e, context)
    
    def _should_execute_step(self, step: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """判断是否应该执行某个步骤"""
        return step.get('required', True)
    
    def _format_final_result(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """格式化最终结果"""
        return {
            "status": "success",
            "results": context.get('results', {}),
            "workflow": self.config.get('workflow', {}).get('name', 'Unknown')
        }
    
    def _handle_workflow_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """处理工作流错误"""
        return {
            "status": "error",
            "error_message": str(error),
            "partial_results": context.get('results', {}),
            "workflow": self.config.get('workflow', {}).get('name', 'Unknown')
        }

