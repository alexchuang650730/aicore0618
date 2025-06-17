#!/usr/bin/env python3
"""
飞书消息接收webhook处理器
用于接收飞书群组消息并转发给智能体系统
"""

from flask import Flask, request, jsonify
import json
import requests
import hashlib
import hmac
import base64
from typing import Dict, Any

class FeishuWebhookHandler:
    """飞书Webhook处理器"""
    
    def __init__(self, verification_token: str = None, encrypt_key: str = None):
        self.verification_token = verification_token
        self.encrypt_key = encrypt_key
        self.powerautomation_api = "http://localhost:5001"
    
    def verify_signature(self, timestamp: str, nonce: str, body: str, signature: str) -> bool:
        """验证飞书webhook签名"""
        if not self.encrypt_key:
            return True  # 如果没有配置加密key，跳过验证
        
        # 构造签名字符串
        string_to_sign = f"{timestamp}{nonce}{self.encrypt_key}{body}"
        
        # 计算签名
        calculated_signature = base64.b64encode(
            hashlib.sha256(string_to_sign.encode()).digest()
        ).decode()
        
        return calculated_signature == signature
    
    def handle_message_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """处理消息事件"""
        try:
            # 提取消息信息
            message = event_data.get("event", {})
            message_type = message.get("message_type", "")
            
            # 只处理文本消息
            if message_type != "text":
                return {"success": True, "message": "非文本消息，忽略"}
            
            # 提取消息内容
            content = json.loads(message.get("message", {}).get("content", "{}"))
            text = content.get("text", "").strip()
            
            # 检查是否是智能体命令
            if text.startswith("@"):
                # 转发给PowerAutomation API处理
                response = requests.post(
                    f"{self.powerautomation_api}/api/feishu/agent-message",
                    json={"message": text},
                    timeout=30
                )
                
                if response.status_code == 200:
                    return {"success": True, "message": "智能体命令已处理"}
                else:
                    return {"success": False, "error": f"API调用失败: {response.status_code}"}
            
            return {"success": True, "message": "非智能体命令，忽略"}
            
        except Exception as e:
            return {"success": False, "error": f"处理消息事件失败: {str(e)}"}
    
    def handle_webhook(self, request_data: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
        """处理webhook请求"""
        try:
            # 验证token
            if self.verification_token:
                token = headers.get("X-Lark-Request-Token", "")
                if token != self.verification_token:
                    return {"success": False, "error": "Token验证失败"}
            
            # 处理不同类型的事件
            event_type = request_data.get("type", "")
            
            if event_type == "url_verification":
                # URL验证
                challenge = request_data.get("challenge", "")
                return {"challenge": challenge}
            
            elif event_type == "event_callback":
                # 事件回调
                event = request_data.get("event", {})
                event_type = event.get("type", "")
                
                if event_type == "message":
                    return self.handle_message_event(request_data)
                else:
                    return {"success": True, "message": f"未处理的事件类型: {event_type}"}
            
            else:
                return {"success": True, "message": f"未处理的请求类型: {event_type}"}
                
        except Exception as e:
            return {"success": False, "error": f"处理webhook失败: {str(e)}"}

# 全局webhook处理器实例
webhook_handler = FeishuWebhookHandler()

def setup_webhook_routes(app: Flask):
    """设置webhook路由"""
    
    @app.route('/webhook/feishu', methods=['POST'])
    def feishu_webhook():
        """飞书webhook端点"""
        try:
            # 获取请求数据
            request_data = request.get_json()
            headers = dict(request.headers)
            
            # 处理webhook
            result = webhook_handler.handle_webhook(request_data, headers)
            
            return jsonify(result)
            
        except Exception as e:
            return jsonify({
                "success": False,
                "error": f"Webhook处理失败: {str(e)}"
            }), 500

