#!/usr/bin/env python3
"""
飞书群组配置更新工具
用于更新PowerAutomation系统中的飞书群组ID配置
"""

import os
import sys
import json

def update_group_config(chat_id: str, group_name: str, group_type: str = "dev"):
    """更新群组配置"""
    try:
        print(f"🔧 更新群组配置...")
        print(f"   群组ID: {chat_id}")
        print(f"   群组名称: {group_name}")
        print(f"   配置类型: {group_type}")
        
        # 读取当前的feishu_group_manager.py文件
        config_file = "/opt/powerautomation/smart_ui/feishu_group_manager.py"
        
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 更新群组配置
        # 这里我们更新dev群组的ID为真实的群组ID
        old_id = '"id": "oc_powerauto_dev"'
        new_id = f'"id": "{chat_id}"'
        
        if old_id in content:
            content = content.replace(old_id, new_id)
            print(f"✅ 已更新开发讨论群ID")
        else:
            print(f"⚠️ 未找到默认群组ID配置")
        
        # 写回文件
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ 群组配置更新完成")
        
        # 创建群组配置记录文件
        group_config = {
            "updated_at": "2025-06-16T19:00:00",
            "groups": {
                group_type: {
                    "id": chat_id,
                    "name": group_name,
                    "configured": True
                }
            }
        }
        
        with open("/opt/powerautomation/smart_ui/group_config.json", 'w', encoding='utf-8') as f:
            json.dump(group_config, f, indent=2, ensure_ascii=False)
        
        print(f"📝 配置记录已保存到 group_config.json")
        
        return True
        
    except Exception as e:
        print(f"❌ 更新配置失败: {e}")
        return False

def main():
    print("🔧 飞书群组配置更新工具")
    print("=" * 50)
    
    if len(sys.argv) < 3:
        print(f"📋 使用方法:")
        print(f"   python3 update_group_config.py <群组ID> <群组名称> [类型]")
        print(f"")
        print(f"📝 示例:")
        print(f"   python3 update_group_config.py \"oc_123456789\" \"PowerAutomation开发群\" \"dev\"")
        return
    
    chat_id = sys.argv[1]
    group_name = sys.argv[2]
    group_type = sys.argv[3] if len(sys.argv) > 3 else "dev"
    
    if update_group_config(chat_id, group_name, group_type):
        print(f"\n🎉 配置更新成功！")
        print(f"📝 下一步操作:")
        print(f"   1. 重启API服务器: pkill -f api_server.py && FEISHU_APP_ID=\"cli_a8da81f628389013\" FEISHU_APP_SECRET=\"JCm0Tozwo9xqoKwofutz7fXUbtGozjwh\" python3 api_server.py &")
        print(f"   2. 测试消息发送: curl -X POST -H 'Content-Type: application/json' -d '{{\"message\": \"测试消息\"}}' http://localhost:5001/api/feishu/send-message")
    else:
        print(f"\n❌ 配置更新失败")

if __name__ == "__main__":
    main()

