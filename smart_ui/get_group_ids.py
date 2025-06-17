#!/usr/bin/env python3
"""
飞书群组ID获取工具
用于获取当前机器人所在的所有群组ID
"""

import os
import requests
import json
from datetime import datetime

def get_group_list():
    """获取机器人所在的群组列表"""
    try:
        # 获取环境变量中的凭证
        app_id = os.environ.get('FEISHU_APP_ID', 'cli_a8da81f628389013')
        app_secret = os.environ.get('FEISHU_APP_SECRET', 'JCm0Tozwo9xqoKwofutz7fXUbtGozjwh')
        
        print(f"🔍 获取飞书群组列表...")
        print(f"   使用App ID: {app_id}")
        
        # 1. 获取access token
        token_url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        token_payload = {
            "app_id": app_id,
            "app_secret": app_secret
        }
        token_headers = {
            "Content-Type": "application/json"
        }
        
        token_response = requests.post(token_url, json=token_payload, headers=token_headers, timeout=10)
        token_result = token_response.json()
        
        if token_result.get("code") != 0:
            print(f"❌ 获取access token失败: {token_result}")
            return
        
        access_token = token_result.get("tenant_access_token")
        print(f"✅ Access token获取成功")
        
        # 2. 获取群组列表
        groups_url = "https://open.feishu.cn/open-apis/im/v1/chats"
        groups_headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # 获取群组列表（分页）
        page_token = ""
        all_groups = []
        
        while True:
            params = {
                "page_size": 50
            }
            if page_token:
                params["page_token"] = page_token
            
            groups_response = requests.get(groups_url, headers=groups_headers, params=params, timeout=10)
            groups_result = groups_response.json()
            
            if groups_result.get("code") != 0:
                print(f"❌ 获取群组列表失败: {groups_result}")
                break
            
            data = groups_result.get("data", {})
            items = data.get("items", [])
            all_groups.extend(items)
            
            # 检查是否还有下一页
            page_token = data.get("page_token", "")
            if not page_token:
                break
        
        print(f"✅ 找到 {len(all_groups)} 个群组")
        print("=" * 60)
        
        # 3. 显示群组信息
        for i, group in enumerate(all_groups, 1):
            chat_id = group.get("chat_id", "")
            name = group.get("name", "未命名群组")
            description = group.get("description", "")
            chat_mode = group.get("chat_mode", "")
            chat_type = group.get("chat_type", "")
            
            print(f"📋 群组 {i}:")
            print(f"   名称: {name}")
            print(f"   ID: {chat_id}")
            print(f"   描述: {description}")
            print(f"   类型: {chat_type} ({chat_mode})")
            print("-" * 40)
        
        # 4. 生成配置建议
        if all_groups:
            print(f"\n🔧 配置建议:")
            print(f"选择一个群组作为PowerAutomation通知群，然后更新配置：")
            print(f"")
            
            # 查找可能的PowerAutomation相关群组
            powerauto_groups = []
            for group in all_groups:
                name = group.get("name", "").lower()
                if any(keyword in name for keyword in ["powerautomation", "power", "automation", "开发", "通知", "机器人"]):
                    powerauto_groups.append(group)
            
            if powerauto_groups:
                print(f"🎯 推荐的群组（包含相关关键词）:")
                for group in powerauto_groups:
                    print(f"   • {group.get('name')} - {group.get('chat_id')}")
            
            print(f"\n📝 配置命令示例:")
            if all_groups:
                example_group = all_groups[0]
                print(f"python3 update_group_config.py \"{example_group.get('chat_id')}\" \"{example_group.get('name')}\"")
        
        return all_groups
        
    except Exception as e:
        print(f"❌ 获取群组列表异常: {e}")
        return None

def main():
    print("🚀 飞书群组ID获取工具")
    print("=" * 50)
    
    groups = get_group_list()
    
    if not groups:
        print(f"\n❌ 未找到任何群组")
        print(f"📝 请确保:")
        print(f"   1. PowerAutomation机器人已添加到群组中")
        print(f"   2. 机器人有获取群组信息的权限")
        print(f"   3. 应用已正确配置和发布")
    else:
        print(f"\n✅ 群组信息获取完成！")
        print(f"📋 请选择一个群组作为PowerAutomation通知群")
        print(f"🔧 然后运行配置工具更新群组ID")

if __name__ == "__main__":
    main()

