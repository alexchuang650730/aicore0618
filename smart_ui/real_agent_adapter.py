#!/usr/bin/env python3
"""
实际智能体适配器
用于连接真实的智能体API服务
"""

import requests
import json
from typing import Dict, Any

class ManusAgentAdapter:
    """Manus智能体适配器"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
    
    def call_agent(self, message: str, include_context: bool = True) -> Dict[str, Any]:
        """调用Manus智能体"""
        try:
            # 使用form-data格式发送请求
            data = {
                'message': message,
                'include_manus_context': str(include_context).lower()
            }
            
            response = requests.post(
                f"{self.base_url}/chat",
                files=data,  # 使用files参数发送form-data
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "response": result.get("response", ""),
                    "conversation_history": result.get("conversation_history", []),
                    "model_used": result.get("model_used", "unknown"),
                    "raw_result": result
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"调用智能体失败: {str(e)}"
            }

# 实际智能体配置
REAL_AGENTS = {
    "manus_general": {
        "name": "Manus通用智能体",
        "description": "Manus通用智能体 - 支持各种任务和问题解答",
        "adapter": ManusAgentAdapter("https://8000-ikvts05khp07qmlozkmc6-61267dc1.manusvm.computer"),
        "command_prefix": "@manus",
        "icon": "🤖",
        "color": "#00d4aa"
    }
}

def call_real_agent(agent_key: str, message: str) -> Dict[str, Any]:
    """调用实际的智能体"""
    if agent_key not in REAL_AGENTS:
        return {
            "success": False,
            "error": f"智能体 {agent_key} 不存在"
        }
    
    agent_config = REAL_AGENTS[agent_key]
    adapter = agent_config["adapter"]
    
    return adapter.call_agent(message)

