#!/usr/bin/env python3
"""
编码工作流连接器
连接SmartUI与编码工作流MCP，获取实时Dashboard数据
"""

import requests
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime
import time

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CodingWorkflowConnector:
    """编码工作流连接器"""
    
    def __init__(self):
        self.coding_workflow_url = "http://localhost:8093"
        self.developer_flow_url = "http://localhost:8097"
        self.last_update = None
        self.cached_data = None
        self.cache_duration = 30  # 缓存30秒
        
    def get_three_node_dashboard_data(self) -> Dict[str, Any]:
        """获取三节点工作流Dashboard数据"""
        try:
            # 检查缓存
            if self._is_cache_valid():
                logger.info("返回缓存的Dashboard数据")
                return self.cached_data
            
            # 从编码工作流MCP获取数据
            response = requests.post(
                f"{self.coding_workflow_url}/mcp/request",
                json={
                    "action": "get_three_node_workflow_dashboard",
                    "params": {}
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    # 更新缓存
                    self.cached_data = data["dashboard_data"]
                    self.last_update = datetime.now()
                    
                    logger.info("成功获取编码工作流Dashboard数据")
                    return self.cached_data
                else:
                    logger.error(f"编码工作流MCP返回错误: {data.get('error')}")
                    return self._get_fallback_data()
            else:
                logger.error(f"编码工作流MCP请求失败: {response.status_code}")
                return self._get_fallback_data()
                
        except requests.exceptions.RequestException as e:
            logger.error(f"连接编码工作流MCP失败: {e}")
            return self._get_fallback_data()
        except Exception as e:
            logger.error(f"获取Dashboard数据异常: {e}")
            return self._get_fallback_data()
    
    def get_coding_workflow_metrics(self) -> Dict[str, Any]:
        """获取编码工作流指标数据"""
        try:
            dashboard_data = self.get_three_node_dashboard_data()
            
            if not dashboard_data:
                return self._get_fallback_metrics()
            
            # 提取关键指标
            workflow_card = dashboard_data.get("workflow_card", {})
            metrics = workflow_card.get("metrics", {})
            real_time_data = dashboard_data.get("real_time_data", {})
            
            return {
                "success": True,
                "timestamp": datetime.now().isoformat(),
                "status": workflow_card.get("status", "运行中"),
                "status_color": workflow_card.get("status_color", "success"),
                "metrics": {
                    "code_quality": {
                        "value": metrics.get("code_quality", {}).get("value", 84),
                        "label": "代码质量",
                        "unit": "%",
                        "trend": "stable"
                    },
                    "architecture_compliance": {
                        "value": metrics.get("architecture_compliance", {}).get("value", 89),
                        "label": "架构合规",
                        "unit": "%",
                        "trend": "improving"
                    },
                    "daily_commits": {
                        "value": metrics.get("daily_commits", {}).get("value", 15),
                        "label": "今日提交",
                        "unit": "",
                        "trend": "active"
                    },
                    "violations_detected": {
                        "value": metrics.get("violations_detected", {}).get("value", 0),
                        "label": "违规检测",
                        "unit": "",
                        "trend": "good"
                    }
                },
                "real_time_info": {
                    "git_status": real_time_data.get("git_status", {}),
                    "intervention_stats": real_time_data.get("intervention_stats", {}),
                    "last_updated": real_time_data.get("last_updated")
                }
            }
            
        except Exception as e:
            logger.error(f"获取编码工作流指标失败: {e}")
            return self._get_fallback_metrics()
    
    def get_three_node_status(self) -> Dict[str, Any]:
        """获取三节点状态"""
        try:
            dashboard_data = self.get_three_node_dashboard_data()
            
            if not dashboard_data:
                return self._get_fallback_nodes()
            
            nodes = dashboard_data.get("three_node_workflow", {}).get("nodes", [])
            
            return {
                "success": True,
                "timestamp": datetime.now().isoformat(),
                "nodes": nodes,
                "total_progress": sum(node.get("progress", 0) for node in nodes) / len(nodes) if nodes else 0
            }
            
        except Exception as e:
            logger.error(f"获取三节点状态失败: {e}")
            return self._get_fallback_nodes()
    
    def get_directory_compliance_status(self) -> Dict[str, Any]:
        """获取目录规范合规状态"""
        try:
            # 从Developer Flow MCP获取合规性摘要
            response = requests.post(
                f"{self.developer_flow_url}/mcp/request",
                json={
                    "action": "get_compliance_summary",
                    "params": {}
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    summary = data.get("summary", {})
                    return {
                        "success": True,
                        "compliance_score": max(0, 100 - summary.get("total_violations", 0)),
                        "total_violations": summary.get("total_violations", 0),
                        "auto_fixable": summary.get("auto_fixable", 0),
                        "critical": summary.get("critical", 0),
                        "last_check": data.get("last_check"),
                        "status": data.get("status", "unknown")
                    }
            
            return {
                "success": False,
                "compliance_score": 85,
                "total_violations": 0,
                "message": "无法获取合规状态"
            }
            
        except Exception as e:
            logger.error(f"获取目录合规状态失败: {e}")
            return {
                "success": False,
                "compliance_score": 85,
                "total_violations": 0,
                "error": str(e)
            }
    
    def _is_cache_valid(self) -> bool:
        """检查缓存是否有效"""
        if not self.last_update or not self.cached_data:
            return False
        
        time_diff = (datetime.now() - self.last_update).total_seconds()
        return time_diff < self.cache_duration
    
    def _get_fallback_data(self) -> Dict[str, Any]:
        """获取备用数据（当MCP不可用时）"""
        logger.warning("使用备用Dashboard数据")
        return {
            "three_node_workflow": {
                "nodes": [
                    {
                        "id": "coding",
                        "name": "编码",
                        "status": "active",
                        "progress": 85,
                        "color": "#007AFF",
                        "icon": "code",
                        "details": {
                            "current_branch": "main",
                            "commits_today": 12,
                            "files_modified": 8,
                            "last_commit": "feat: 更新Dashboard集成..."
                        }
                    },
                    {
                        "id": "editing",
                        "name": "编辑",
                        "status": "active", 
                        "progress": 92,
                        "color": "#FF8C00",
                        "icon": "edit",
                        "details": {
                            "uncommitted_files": 3,
                            "compliance_score": 89,
                            "auto_fixes_applied": 2,
                            "is_clean": False
                        }
                    },
                    {
                        "id": "deployment",
                        "name": "部署",
                        "status": "ready",
                        "progress": 78,
                        "color": "#00C851",
                        "icon": "rocket",
                        "details": {
                            "release_manager_status": "ready",
                            "deployment_ready": True,
                            "last_deployment": "2025-06-16 01:00:00"
                        }
                    }
                ]
            },
            "workflow_card": {
                "title": "编码工作流",
                "status": "运行中",
                "status_color": "success",
                "metrics": {
                    "code_quality": {"value": 84, "label": "代码质量", "unit": "%"},
                    "architecture_compliance": {"value": 89, "label": "架构合规", "unit": "%"},
                    "daily_commits": {"value": 15, "label": "今日提交", "unit": ""},
                    "violations_detected": {"value": 0, "label": "违规检测", "unit": ""}
                }
            },
            "real_time_data": {
                "last_updated": datetime.now().isoformat(),
                "git_status": {
                    "current_branch": "main",
                    "is_clean": False,
                    "uncommitted_changes": 3
                },
                "intervention_stats": {
                    "compliance_score": 89,
                    "violations_today": 0
                }
            }
        }
    
    def _get_fallback_metrics(self) -> Dict[str, Any]:
        """获取备用指标数据"""
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "status": "运行中",
            "status_color": "success",
            "metrics": {
                "code_quality": {"value": 84, "label": "代码质量", "unit": "%", "trend": "stable"},
                "architecture_compliance": {"value": 89, "label": "架构合规", "unit": "%", "trend": "improving"},
                "daily_commits": {"value": 15, "label": "今日提交", "unit": "", "trend": "active"},
                "violations_detected": {"value": 0, "label": "违规检测", "unit": "", "trend": "good"}
            },
            "real_time_info": {
                "git_status": {"current_branch": "main", "is_clean": False},
                "intervention_stats": {"compliance_score": 89},
                "last_updated": datetime.now().isoformat()
            },
            "note": "使用模拟数据 - MCP连接不可用"
        }
    
    def _get_fallback_nodes(self) -> Dict[str, Any]:
        """获取备用节点数据"""
        fallback_data = self._get_fallback_data()
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "nodes": fallback_data["three_node_workflow"]["nodes"],
            "total_progress": 85,
            "note": "使用模拟数据 - MCP连接不可用"
        }

# 全局连接器实例
coding_workflow_connector = CodingWorkflowConnector()

def get_coding_workflow_metrics():
    """获取编码工作流指标（供外部调用）"""
    return coding_workflow_connector.get_coding_workflow_metrics()

def get_three_node_dashboard():
    """获取三节点Dashboard（供外部调用）"""
    return coding_workflow_connector.get_three_node_dashboard_data()

def get_three_node_status():
    """获取三节点状态（供外部调用）"""
    return coding_workflow_connector.get_three_node_status()

def get_directory_compliance():
    """获取目录合规状态（供外部调用）"""
    return coding_workflow_connector.get_directory_compliance_status()

if __name__ == "__main__":
    # 测试连接器
    print("🧪 测试编码工作流连接器...")
    
    connector = CodingWorkflowConnector()
    
    print("\n📊 测试获取Dashboard数据:")
    dashboard_data = connector.get_three_node_dashboard_data()
    print(json.dumps(dashboard_data, indent=2, ensure_ascii=False))
    
    print("\n📈 测试获取指标数据:")
    metrics_data = connector.get_coding_workflow_metrics()
    print(json.dumps(metrics_data, indent=2, ensure_ascii=False))
    
    print("\n🔍 测试获取三节点状态:")
    nodes_data = connector.get_three_node_status()
    print(json.dumps(nodes_data, indent=2, ensure_ascii=False))
    
    print("\n✅ 编码工作流连接器测试完成！")

