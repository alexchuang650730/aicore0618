#!/usr/bin/env python3
"""
Product Orchestrator V3 管理界面启动脚本
专门为远程部署优化
"""

import sys
import os
from pathlib import Path

# 添加项目路径
project_root = Path("/opt/powerautomation")
sys.path.insert(0, str(project_root))

# 设置环境变量
os.environ['FLASK_ENV'] = 'production'

try:
    from admin_dashboard_server import app
    
    if __name__ == '__main__':
        print("🚀 Starting Product Orchestrator V3 Admin Dashboard on port 5001...")
        app.run(
            host='0.0.0.0',
            port=5001,
            debug=False,
            threaded=True,
            use_reloader=False
        )
except Exception as e:
    print(f"❌ Error starting admin dashboard: {e}")
    import traceback
    traceback.print_exc()

