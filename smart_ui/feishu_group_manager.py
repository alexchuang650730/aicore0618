"""
飞书群组管理模块
为SmartUI提供飞书群组切换和管理功能
"""

import os
import json
import requests
from datetime import datetime
from typing import Dict, List, Optional

class FeishuGroupManager:
    """飞书群组管理器"""
    
    def __init__(self, app_id: str, app_secret: str):
        self.app_id = app_id
        self.app_secret = app_secret
        self.base_url = "https://open.feishu.cn/open-apis"
        self.access_token = None
        self.token_expires_at = 0  # token过期时间戳
        self.current_group = "dev"  # 默认当前群组
        
        # 飞书群组配置
        self.groups = {
            "dev": {
                "id": "oc_d9594af12d2bcb4e35df3019a71cf1d2",
                "name": "开发讨论群",
                "description": "日常开发交流和技术讨论",
                "icon": "💻",
                "color": "#3b82f6"
            },
            "architecture": {
                "id": "oc_powerauto_arch", 
                "name": "架构决策群",
                "description": "重要架构决策和设计讨论",
                "icon": "🏗️",
                "color": "#8b5cf6"
            },
            "pr_review": {
                "id": "oc_powerauto_pr",
                "name": "代码审查群", 
                "description": "PR审查通知和代码质量讨论",
                "icon": "🔍",
                "color": "#f59e0b"
            },
            "deployment": {
                "id": "oc_powerauto_deploy",
                "name": "部署监控群",
                "description": "部署状态更新和监控告警",
                "icon": "🚀",
                "color": "#10b981"
            },
            "smart_ui": {
                "id": "oc_powerauto_ui",
                "name": "智慧UI群",
                "description": "UI相关通知和用户反馈",
                "icon": "🎨", 
                "color": "#ef4444"
            }
        }
    
    def get_access_token(self) -> Optional[str]:
        """获取飞书访问令牌 - 支持真实凭证和自动刷新"""
        try:
            # 检查当前token是否有效且未过期
            current_time = datetime.now().timestamp()
            if (self.access_token and 
                self.access_token != "test_access_token" and 
                current_time < self.token_expires_at - 300):  # 提前5分钟刷新
                return self.access_token
            
            url = f"{self.base_url}/auth/v3/tenant_access_token/internal"
            payload = {
                "app_id": self.app_id,
                "app_secret": self.app_secret
            }
            
            headers = {
                "Content-Type": "application/json"
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=10)
            result = response.json()
            
            if result.get("code") == 0:
                self.access_token = result.get("tenant_access_token")
                # 记录token获取时间（实际应该存储过期时间）
                self.token_expires_at = datetime.now().timestamp() + 7200  # 2小时后过期
                print(f"✅ 飞书访问令牌获取成功: {self.access_token[:20]}...")
                return self.access_token
            else:
                error_msg = result.get("msg", "未知错误")
                print(f"❌ 获取飞书访问令牌失败: {error_msg}")
                print(f"   错误码: {result.get('code')}")
                print(f"   使用的App ID: {self.app_id}")
                
                # 如果是测试凭证，返回模拟token
                if self.app_id == "cli_test_app_id":
                    print("🧪 使用测试凭证，返回模拟token")
                    self.access_token = "test_access_token"
                    return self.access_token
                
                return None
        except Exception as e:
            print(f"❌ 飞书API调用异常: {e}")
            # 如果是测试环境，返回模拟token
            if self.app_id == "cli_test_app_id":
                print("🧪 异常情况下使用测试token")
                self.access_token = "test_access_token"
                return self.access_token
            return None
    
    def get_group_info(self, group_key: str) -> Dict:
        """获取群组信息"""
        if group_key not in self.groups:
            return {"error": "群组不存在"}
        
        group = self.groups[group_key].copy()
        group["key"] = group_key
        group["is_current"] = group_key == self.current_group
        
        # 模拟群组状态数据（实际应该从飞书API获取）
        group["status"] = {
            "online_members": 12 if group_key == "dev" else 8,
            "total_members": 15 if group_key == "dev" else 10,
            "last_message_time": datetime.now().strftime("%H:%M"),
            "unread_count": 3 if group_key == self.current_group else 0
        }
        
        return group
    
    def get_all_groups(self) -> List[Dict]:
        """获取所有群组信息"""
        groups_info = []
        for group_key in self.groups.keys():
            groups_info.append(self.get_group_info(group_key))
        return groups_info
    
    def switch_group(self, group_key: str) -> Dict:
        """切换当前活跃群组"""
        if group_key not in self.groups:
            return {"success": False, "message": "群组不存在"}
        
        old_group = self.current_group
        self.current_group = group_key
        
        return {
            "success": True,
            "message": f"已切换到{self.groups[group_key]['name']}",
            "old_group": old_group,
            "new_group": group_key,
            "group_info": self.get_group_info(group_key)
        }
    
    def get_group_status(self) -> Dict:
        """获取群组状态统计"""
        total_notifications = 0
        active_groups = 0
        
        for group_key in self.groups.keys():
            group_info = self.get_group_info(group_key)
            if group_info["status"]["online_members"] > 0:
                active_groups += 1
            total_notifications += group_info["status"]["unread_count"]
        
        return {
            "current_group": self.get_group_info(self.current_group),
            "total_notifications": total_notifications,
            "active_groups": active_groups,
            "total_groups": len(self.groups),
            "last_update": datetime.now().isoformat()
        }
    
    def send_message_to_current_group(self, message: str) -> Dict:
        """向当前群组发送消息"""
        if not self.access_token:
            self.get_access_token()
        
        current_group_id = self.groups[self.current_group]["id"]
        
        try:
            # 使用URL参数方式传递receive_id_type
            url = f"{self.base_url}/im/v1/messages?receive_id_type=chat_id"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            payload = {
                "receive_id": current_group_id,
                "msg_type": "text",
                "content": json.dumps({"text": message})
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=10)
            result = response.json()
            
            return {
                "success": result.get("code") == 0,
                "group": self.groups[self.current_group]["name"],
                "message": message,
                "result": result
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

# 全局飞书群组管理器实例
feishu_manager = None

def get_feishu_manager():
    """获取飞书群组管理器实例"""
    global feishu_manager
    if feishu_manager is None:
        app_id = os.getenv('FEISHU_APP_ID', 'default_app_id')
        app_secret = os.getenv('FEISHU_APP_SECRET', 'default_secret')
        feishu_manager = FeishuGroupManager(app_id, app_secret)
    return feishu_manager

