#!/usr/bin/env python3
"""
多智能体管理器
用于管理和调度不同类型的智能体
"""

import os
import json
import requests
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class AgentConfig:
    """智能体配置"""
    name: str
    description: str
    api_endpoint: str
    command_prefix: str
    icon: str
    color: str
    timeout: int = 30
    enabled: bool = True

class MultiAgentManager:
    """多智能体管理器"""
    
    def __init__(self):
        self.agents = {}
        self.load_agent_configs()
    
    def load_agent_configs(self):
        """加载智能体配置"""
        # 预定义的智能体配置
        default_agents = [
            AgentConfig(
                name="personal_agent",
                description="个人版智能体 - 个人项目和学习辅助",
                api_endpoint="http://localhost:8001/api/personal",
                command_prefix="@personal",
                icon="💻",
                color="#00d4aa",
                timeout=30
            ),
            AgentConfig(
                name="enterprise_agent", 
                description="企业版智能体 - 企业级解决方案和管理",
                api_endpoint="http://localhost:8002/api/enterprise",
                command_prefix="@enterprise",
                icon="📊",
                color="#ff6b6b",
                timeout=45
            ),
            AgentConfig(
                name="analysis_agent",
                description="需求分析智能体 - 业务需求分析和规划",
                api_endpoint="http://localhost:8003/api/analysis", 
                command_prefix="@analysis",
                icon="🎨",
                color="#4ecdc4",
                timeout=40
            ),
            AgentConfig(
                name="design_agent",
                description="设计工作流智能体 - 系统设计和架构规划",
                api_endpoint="http://localhost:8004/api/design",
                command_prefix="@design", 
                icon="⚡",
                color="#45b7d1",
                timeout=35
            ),
            AgentConfig(
                name="code_agent",
                description="代码开发智能体 - 编写、调试、优化代码",
                api_endpoint="http://localhost:8005/api/code",
                command_prefix="@code",
                icon="💻",
                color="#2ecc71",
                timeout=60
            ),
            AgentConfig(
                name="test_agent",
                description="测试智能体 - 自动化测试和质量保证",
                api_endpoint="http://localhost:8006/api/test",
                command_prefix="@test",
                icon="🧪",
                color="#f39c12",
                timeout=35
            ),
            AgentConfig(
                name="deploy_agent",
                description="部署智能体 - 应用部署和发布管理",
                api_endpoint="http://localhost:8007/api/deploy",
                command_prefix="@deploy",
                icon="📊",
                color="#9b59b6",
                timeout=50
            ),
            AgentConfig(
                name="ops_agent",
                description="运维智能体 - 系统监控和运维管理",
                api_endpoint="http://localhost:8008/api/ops",
                command_prefix="@ops",
                icon="🧪",
                color="#e74c3c",
                timeout=40
            ),
            AgentConfig(
                name="doc_agent",
                description="文档中心智能体 - 技术文档和API文档生成",
                api_endpoint="http://localhost:8009/api/doc",
                command_prefix="@doc",
                icon="📝",
                color="#6c5ce7",
                timeout=25
            )
        ]
        
        for agent in default_agents:
            self.agents[agent.name] = agent
    
    def parse_command(self, message: str) -> Optional[Dict[str, Any]]:
        """解析群组命令"""
        message = message.strip()
        
        for agent_name, agent in self.agents.items():
            if message.startswith(agent.command_prefix):
                # 提取命令内容
                command_content = message[len(agent.command_prefix):].strip()
                
                return {
                    "agent_name": agent_name,
                    "agent": agent,
                    "command": command_content,
                    "original_message": message
                }
        
        return None
    
    async def call_agent(self, agent: AgentConfig, command: str, context: Dict = None) -> Dict[str, Any]:
        """调用智能体API"""
        try:
            payload = {
                "command": command,
                "context": context or {},
                "timestamp": datetime.now().isoformat(),
                "source": "feishu_group"
            }
            
            print(f"🤖 调用 {agent.name}: {command[:50]}...")
            
            # 检查智能体是否在线
            health_check = await self.check_agent_health(agent)
            if not health_check["online"]:
                return {
                    "success": False,
                    "error": f"智能体 {agent.name} 当前离线",
                    "agent_name": agent.name
                }
            
            # 调用智能体API
            response = requests.post(
                agent.api_endpoint,
                json=payload,
                timeout=agent.timeout,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "agent_name": agent.name,
                    "agent_icon": agent.icon,
                    "result": result,
                    "response_time": response.elapsed.total_seconds()
                }
            else:
                return {
                    "success": False,
                    "error": f"API调用失败: HTTP {response.status_code}",
                    "agent_name": agent.name
                }
                
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": f"智能体 {agent.name} 响应超时",
                "agent_name": agent.name
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"调用智能体时发生错误: {str(e)}",
                "agent_name": agent.name
            }
    
    async def check_agent_health(self, agent: AgentConfig) -> Dict[str, Any]:
        """检查智能体健康状态"""
        try:
            health_url = agent.api_endpoint.replace("/api/", "/health/")
            response = requests.get(health_url, timeout=5)
            return {
                "online": response.status_code == 200,
                "response_time": response.elapsed.total_seconds()
            }
        except:
            return {"online": False, "response_time": None}
    
    def format_agent_response(self, response: Dict[str, Any]) -> str:
        """格式化智能体响应"""
        if not response["success"]:
            return f"❌ {response['agent_name']} 调用失败: {response['error']}"
        
        agent_name = response["agent_name"]
        agent_icon = response.get("agent_icon", "🤖")
        result = response["result"]
        response_time = response.get("response_time", 0)
        
        # 格式化响应内容
        if isinstance(result, dict):
            if "message" in result:
                content = result["message"]
            elif "result" in result:
                content = result["result"]
            else:
                content = json.dumps(result, indent=2, ensure_ascii=False)
        else:
            content = str(result)
        
        return f"""{agent_icon} **{agent_name}** 响应 (耗时: {response_time:.2f}s)

{content}

---
💡 如需更多帮助，请使用相应的命令前缀"""
    
    def get_agent_list(self) -> str:
        """获取智能体列表"""
        agent_list = "🤖 **可用智能体列表**\n\n"
        
        for agent in self.agents.values():
            status = "🟢" if agent.enabled else "🔴"
            agent_list += f"{status} {agent.icon} **{agent.command_prefix}** - {agent.description}\n"
        
        agent_list += "\n💡 **使用方法**: 在消息前加上对应的命令前缀\n"
        agent_list += "📝 **示例**: `@code 写一个计算器函数`"
        
        return agent_list
    
    def get_agent_status(self) -> Dict[str, Any]:
        """获取所有智能体状态"""
        return {
            "total_agents": len(self.agents),
            "enabled_agents": len([a for a in self.agents.values() if a.enabled]),
            "agents": {
                name: {
                    "name": agent.name,
                    "description": agent.description,
                    "command_prefix": agent.command_prefix,
                    "icon": agent.icon,
                    "color": agent.color,
                    "enabled": agent.enabled,
                    "endpoint": agent.api_endpoint
                }
                for name, agent in self.agents.items()
            }
        }

# 全局多智能体管理器实例
multi_agent_manager = None

def get_multi_agent_manager():
    """获取多智能体管理器实例"""
    global multi_agent_manager
    if multi_agent_manager is None:
        multi_agent_manager = MultiAgentManager()
    return multi_agent_manager

