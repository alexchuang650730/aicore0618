#!/usr/bin/env python3
"""
飞书长连接服务启动脚本
独立运行飞书长连接客户端
"""

import asyncio
import os
import sys
import logging
from pathlib import Path

# 添加项目路径
sys.path.append('/opt/powerautomation/smart_ui')

from feishu_long_connection import initialize_feishu_client, get_feishu_client

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """主函数"""
    print("🚀 启动飞书长连接服务...")
    
    # 从环境变量或配置文件读取凭证
    app_id = os.getenv('FEISHU_APP_ID', 'cli_test_app_id')
    app_secret = os.getenv('FEISHU_APP_SECRET', 'test_app_secret')
    
    if app_id == 'cli_test_app_id':
        print("⚠️  使用测试凭证，请设置环境变量:")
        print("   export FEISHU_APP_ID='your_app_id'")
        print("   export FEISHU_APP_SECRET='your_app_secret'")
        print()
    
    # 初始化飞书客户端
    success = await initialize_feishu_client(app_id, app_secret)
    
    if success:
        print("✅ 飞书长连接客户端启动成功!")
        print("📱 现在可以在飞书应用中开启长连接模式了")
        print()
        print("🔗 连接状态: 已连接")
        print("📊 支持的群组: 5个")
        print("🎯 功能: GitHub事件通知、群组切换、消息发送")
        print()
        print("按 Ctrl+C 停止服务...")
        
        try:
            # 保持服务运行
            while True:
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            print("\n🛑 正在停止飞书长连接服务...")
            client = get_feishu_client()
            if client:
                await client.stop()
            print("✅ 服务已停止")
            
    else:
        print("❌ 飞书长连接客户端启动失败!")
        print("请检查:")
        print("1. 网络连接是否正常")
        print("2. App ID 和 App Secret 是否正确")
        print("3. 飞书应用权限是否配置正确")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"服务启动失败: {e}")
        sys.exit(1)

