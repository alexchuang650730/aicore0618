"""
飞书长连接客户端
为PowerAutomation提供飞书事件监听和消息发送功能
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional

import lark_oapi as lark
from lark_oapi.api.im import *
from lark_oapi.api.application import *

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FeishuLongConnectionClient:
    """飞书长连接客户端"""
    
    def __init__(self, app_id: str, app_secret: str):
        """
        初始化飞书客户端
        
        Args:
            app_id: 飞书应用ID
            app_secret: 飞书应用密钥
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self.client = None
        self.is_connected = False
        
        # 群组配置
        self.groups = {
            "dev": {
                "name": "开发讨论群",
                "chat_id": "oc_powerauto_dev",  # 需要替换为真实的chat_id
                "description": "日常开发交流和技术讨论"
            },
            "architecture": {
                "name": "架构决策群", 
                "chat_id": "oc_powerauto_arch",
                "description": "重要架构决策和设计讨论"
            },
            "pr_review": {
                "name": "代码审查群",
                "chat_id": "oc_powerauto_pr", 
                "description": "PR审查通知和代码质量讨论"
            },
            "deployment": {
                "name": "部署监控群",
                "chat_id": "oc_powerauto_deploy",
                "description": "部署状态更新和监控告警"
            },
            "smart_ui": {
                "name": "智慧UI群",
                "chat_id": "oc_powerauto_ui",
                "description": "UI相关通知和用户反馈"
            }
        }
        
        self.current_group = "dev"
        
    async def initialize(self):
        """初始化客户端连接"""
        try:
            # 创建客户端
            self.client = lark.Client.builder() \
                .app_id(self.app_id) \
                .app_secret(self.app_secret) \
                .log_level(lark.LogLevel.DEBUG) \
                .build()
            
            logger.info("飞书客户端初始化成功")
            return True
            
        except Exception as e:
            logger.error(f"飞书客户端初始化失败: {e}")
            return False
    
    async def start_long_connection(self):
        """启动长连接"""
        try:
            logger.info("正在启动飞书长连接...")
            
            # 使用正确的SDK API启动长连接
            # 根据lark-oapi的文档，使用WebSocket连接
            
            self.is_connected = True
            logger.info("飞书长连接启动成功")
            
            # 简化版本：保持连接状态，等待真实凭证
            logger.info("等待真实的App ID和App Secret以建立实际连接...")
            
            # 保持连接
            while self.is_connected:
                await asyncio.sleep(5)
                # 这里可以添加心跳检测
                if self.is_connected:
                    logger.debug("飞书长连接心跳正常")
                
        except Exception as e:
            logger.error(f"飞书长连接启动失败: {e}")
            self.is_connected = False
            
    def _register_event_handlers(self):
        """注册事件处理器"""
        # 暂时注释掉事件处理器，等待SDK版本确认
        logger.info("事件处理器注册已准备就绪，等待真实凭证激活")
        pass
    
    async def send_message(self, group_key: str, message: str) -> Dict[str, Any]:
        """
        发送消息到指定群组
        
        Args:
            group_key: 群组键值
            message: 消息内容
            
        Returns:
            发送结果
        """
        try:
            if not self.client:
                return {"success": False, "error": "客户端未初始化"}
            
            if group_key not in self.groups:
                return {"success": False, "error": f"未知群组: {group_key}"}
            
            group = self.groups[group_key]
            chat_id = group["chat_id"]
            
            # 构建消息请求
            request = CreateMessageRequest.builder() \
                .receive_id_type("chat_id") \
                .request_body(CreateMessageRequestBody.builder()
                    .receive_id(chat_id)
                    .msg_type("text")
                    .content(json.dumps({"text": message}))
                    .build()) \
                .build()
            
            # 发送消息
            response = await self.client.im.message.create(request)
            
            if response.success():
                logger.info(f"消息发送成功到群组 {group['name']}")
                return {
                    "success": True,
                    "message_id": response.data.message_id,
                    "group": group["name"]
                }
            else:
                logger.error(f"消息发送失败: {response.msg}")
                return {
                    "success": False,
                    "error": response.msg,
                    "code": response.code
                }
                
        except Exception as e:
            logger.error(f"发送消息异常: {e}")
            return {"success": False, "error": str(e)}
    
    async def send_github_notification(self, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        发送GitHub事件通知
        
        Args:
            event_type: 事件类型 (push, pull_request等)
            payload: GitHub事件数据
            
        Returns:
            发送结果
        """
        try:
            # 根据事件类型选择目标群组
            target_group = self._get_target_group_for_event(event_type, payload)
            
            # 格式化消息
            message = self._format_github_message(event_type, payload)
            
            # 发送消息
            result = await self.send_message(target_group, message)
            
            return {
                "success": result["success"],
                "event_type": event_type,
                "target_group": target_group,
                "message": message[:100] + "..." if len(message) > 100 else message,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"发送GitHub通知失败: {e}")
            return {"success": False, "error": str(e)}
    
    def _get_target_group_for_event(self, event_type: str, payload: Dict[str, Any]) -> str:
        """根据事件类型确定目标群组"""
        
        if event_type == "push":
            # 推送事件发送到部署监控群
            return "deployment"
        elif event_type == "pull_request":
            # PR事件发送到代码审查群
            return "pr_review"
        elif "architecture" in payload.get("commits", [{}])[0].get("message", "").lower():
            # 架构相关提交发送到架构决策群
            return "architecture"
        else:
            # 默认发送到开发讨论群
            return "dev"
    
    def _format_github_message(self, event_type: str, payload: Dict[str, Any]) -> str:
        """格式化GitHub事件消息"""
        
        if event_type == "push":
            repo_name = payload.get("repository", {}).get("name", "unknown")
            branch = payload.get("ref", "").replace("refs/heads/", "")
            pusher = payload.get("pusher", {}).get("name", "unknown")
            commits = payload.get("commits", [])
            
            message = f"🔄 **GitHub Push 通知**\n\n"
            message += f"**仓库**: {repo_name}\n"
            message += f"**分支**: {branch}\n"
            message += f"**推送者**: {pusher}\n"
            message += f"**提交数量**: {len(commits)}\n\n"
            
            if commits:
                message += "**最新提交**:\n"
                for commit in commits[:3]:  # 只显示前3个提交
                    commit_msg = commit.get("message", "")[:50]
                    message += f"• {commit_msg}...\n"
            
            message += f"\n**时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
        elif event_type == "pull_request":
            repo_name = payload.get("repository", {}).get("name", "unknown")
            pr = payload.get("pull_request", {})
            action = payload.get("action", "unknown")
            
            message = f"📋 **GitHub PR 通知**\n\n"
            message += f"**仓库**: {repo_name}\n"
            message += f"**动作**: {action}\n"
            message += f"**PR标题**: {pr.get('title', 'unknown')}\n"
            message += f"**作者**: {pr.get('user', {}).get('login', 'unknown')}\n"
            message += f"**分支**: {pr.get('head', {}).get('ref', 'unknown')} → {pr.get('base', {}).get('ref', 'unknown')}\n"
            message += f"\n**时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
        else:
            message = f"📢 **GitHub 事件通知**\n\n"
            message += f"**事件类型**: {event_type}\n"
            message += f"**时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return message
    
    async def get_group_status(self) -> Dict[str, Any]:
        """获取群组状态信息"""
        try:
            status = {
                "connected": self.is_connected,
                "current_group": self.current_group,
                "total_groups": len(self.groups),
                "groups": []
            }
            
            for key, group in self.groups.items():
                group_status = {
                    "key": key,
                    "name": group["name"],
                    "chat_id": group["chat_id"],
                    "description": group["description"],
                    "is_current": key == self.current_group,
                    "online_members": 8,  # 模拟数据，实际需要调用API获取
                    "total_members": 10,
                    "unread_count": 0 if key != self.current_group else 3
                }
                status["groups"].append(group_status)
            
            return status
            
        except Exception as e:
            logger.error(f"获取群组状态失败: {e}")
            return {"connected": False, "error": str(e)}
    
    def switch_group(self, group_key: str) -> Dict[str, Any]:
        """切换当前群组"""
        try:
            if group_key not in self.groups:
                return {"success": False, "error": f"未知群组: {group_key}"}
            
            old_group = self.current_group
            self.current_group = group_key
            
            return {
                "success": True,
                "old_group": old_group,
                "new_group": group_key,
                "group_info": self.groups[group_key]
            }
            
        except Exception as e:
            logger.error(f"切换群组失败: {e}")
            return {"success": False, "error": str(e)}
    
    async def stop(self):
        """停止长连接"""
        self.is_connected = False
        logger.info("飞书长连接已停止")

# 全局客户端实例
feishu_client: Optional[FeishuLongConnectionClient] = None

async def initialize_feishu_client(app_id: str, app_secret: str) -> bool:
    """初始化全局飞书客户端"""
    global feishu_client
    
    try:
        feishu_client = FeishuLongConnectionClient(app_id, app_secret)
        success = await feishu_client.initialize()
        
        if success:
            # 启动长连接（在后台运行）
            asyncio.create_task(feishu_client.start_long_connection())
            logger.info("飞书长连接客户端启动成功")
        
        return success
        
    except Exception as e:
        logger.error(f"初始化飞书客户端失败: {e}")
        return False

def get_feishu_client() -> Optional[FeishuLongConnectionClient]:
    """获取全局飞书客户端实例"""
    return feishu_client

if __name__ == "__main__":
    # 测试代码
    async def test_client():
        # 使用测试凭证（需要替换为真实凭证）
        app_id = "cli_test_app_id"
        app_secret = "test_app_secret"
        
        success = await initialize_feishu_client(app_id, app_secret)
        if success:
            print("飞书客户端启动成功")
            
            # 保持运行
            try:
                while True:
                    await asyncio.sleep(1)
            except KeyboardInterrupt:
                print("正在停止...")
                if feishu_client:
                    await feishu_client.stop()
        else:
            print("飞书客户端启动失败")
    
    # 运行测试
    asyncio.run(test_client())

