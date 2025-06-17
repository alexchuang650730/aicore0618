#!/usr/bin/env python3
"""
飞书应用凭证配置工具
用于设置和验证飞书应用的App ID和App Secret
"""

import os
import sys
import requests
import json
from datetime import datetime

def test_feishu_credentials(app_id: str, app_secret: str) -> bool:
    """测试飞书应用凭证是否有效"""
    try:
        url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
        payload = {
            "app_id": app_id,
            "app_secret": app_secret
        }
        headers = {
            "Content-Type": "application/json"
        }
        
        print(f"🔍 测试飞书应用凭证...")
        print(f"   App ID: {app_id}")
        print(f"   App Secret: {app_secret[:10]}...")
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        result = response.json()
        
        if result.get("code") == 0:
            token = result.get("tenant_access_token")
            print(f"✅ 凭证验证成功！")
            print(f"   获取到的Token: {token[:20]}...")
            print(f"   过期时间: {result.get('expire', 7200)}秒")
            return True
        else:
            print(f"❌ 凭证验证失败！")
            print(f"   错误码: {result.get('code')}")
            print(f"   错误信息: {result.get('msg')}")
            return False
            
    except Exception as e:
        print(f"❌ 网络请求失败: {e}")
        return False

def set_environment_variables(app_id: str, app_secret: str):
    """设置环境变量"""
    print(f"\n🔧 设置环境变量...")
    
    # 设置当前会话的环境变量
    os.environ['FEISHU_APP_ID'] = app_id
    os.environ['FEISHU_APP_SECRET'] = app_secret
    
    # 生成环境变量设置命令
    env_commands = f"""
# 飞书应用凭证环境变量
export FEISHU_APP_ID='{app_id}'
export FEISHU_APP_SECRET='{app_secret}'
"""
    
    # 保存到文件
    with open('/home/ubuntu/.feishu_env', 'w') as f:
        f.write(env_commands)
    
    print(f"✅ 环境变量已设置")
    print(f"   配置文件: /home/ubuntu/.feishu_env")
    print(f"   要永久生效，请运行: source /home/ubuntu/.feishu_env")

def main():
    print("🚀 飞书应用凭证配置工具")
    print("=" * 50)
    
    # 检查命令行参数
    if len(sys.argv) == 3:
        app_id = sys.argv[1]
        app_secret = sys.argv[2]
        print(f"📋 使用命令行参数:")
    else:
        # 交互式输入
        print(f"📋 请输入飞书应用凭证:")
        app_id = input("App ID: ").strip()
        app_secret = input("App Secret: ").strip()
    
    if not app_id or not app_secret:
        print("❌ App ID和App Secret不能为空")
        return
    
    # 测试凭证
    if test_feishu_credentials(app_id, app_secret):
        # 设置环境变量
        set_environment_variables(app_id, app_secret)
        
        print(f"\n🎉 配置完成！")
        print(f"📝 下一步操作:")
        print(f"   1. 重启API服务器: pkill -f api_server.py && python3 /opt/powerautomation/smart_ui/api_server.py &")
        print(f"   2. 测试飞书功能: curl http://localhost:5001/api/feishu/status")
        print(f"   3. 发送测试消息: curl -X POST -H 'Content-Type: application/json' -d '{{\"message\": \"测试消息\"}}' http://localhost:5001/api/feishu/send-message")
    else:
        print(f"\n❌ 配置失败，请检查凭证是否正确")
        print(f"📖 获取凭证的步骤:")
        print(f"   1. 访问 https://open.feishu.cn/")
        print(f"   2. 登录并进入开发者后台")
        print(f"   3. 选择您的应用")
        print(f"   4. 在'基础信息 > 凭证与基础信息'页面获取App ID和App Secret")

if __name__ == "__main__":
    main()

