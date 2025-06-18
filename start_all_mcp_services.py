#!/usr/bin/env python3
"""
PowerAutomation MCP服务启动脚本
一键启动所有7个MCP服务
"""

import subprocess
import time
import sys
import os
from pathlib import Path

# MCP服务配置
MCP_SERVICES = [
    {
        'name': 'Requirements Analysis MCP',
        'script': '/home/ubuntu/aicore0615/mcp/workflow/requirements_analysis_mcp/requirements_analysis_mcp_server.py',
        'port': 8091
    },
    {
        'name': 'Architecture Design MCP', 
        'script': '/home/ubuntu/aicore0615/mcp/workflow/architecture_design_mcp/architecture_design_mcp_server.py',
        'port': 8092
    },
    {
        'name': 'Coding Workflow MCP',
        'script': '/home/ubuntu/aicore0615/mcp/workflow/coding_workflow_mcp/coding_workflow_mcp_server.py',
        'port': 8093
    },
    {
        'name': 'Developer Flow MCP',
        'script': '/home/ubuntu/aicore0615/mcp/workflow/developer_flow_mcp/developer_flow_mcp_server.py',
        'port': 8094
    },
    {
        'name': 'Test Manager MCP',
        'script': '/home/ubuntu/aicore0615/mcp/workflow/test_manager_mcp/test_manager_mcp_clean.py',
        'port': 8097
    },
    {
        'name': 'Release Manager MCP',
        'script': '/home/ubuntu/aicore0615/mcp/workflow/release_manager_mcp/release_manager_mcp_server.py',
        'port': 8096
    },
    {
        'name': 'Operations Workflow MCP',
        'script': '/home/ubuntu/aicore0615/mcp/workflow/operations_workflow_mcp/operations_workflow_mcp_server.py',
        'port': 8090
    }
]

def check_port_available(port):
    """检查端口是否可用"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) != 0

def start_service(service):
    """启动单个服务"""
    script_path = service['script']
    if not os.path.exists(script_path):
        print(f"❌ {service['name']}: 脚本文件不存在 {script_path}")
        return False
    
    if not check_port_available(service['port']):
        print(f"⚠️  {service['name']}: 端口 {service['port']} 已被占用")
        return True  # 认为服务已经在运行
    
    try:
        # 启动服务
        process = subprocess.Popen([
            sys.executable, script_path
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # 等待服务启动
        time.sleep(2)
        
        # 检查服务是否成功启动
        if not check_port_available(service['port']):
            print(f"✅ {service['name']}: 成功启动在端口 {service['port']}")
            return True
        else:
            print(f"❌ {service['name']}: 启动失败")
            return False
            
    except Exception as e:
        print(f"❌ {service['name']}: 启动异常 - {e}")
        return False

def main():
    """主函数"""
    print("🚀 PowerAutomation MCP服务启动器")
    print("=" * 50)
    
    success_count = 0
    total_count = len(MCP_SERVICES)
    
    for service in MCP_SERVICES:
        print(f"启动 {service['name']}...")
        if start_service(service):
            success_count += 1
        time.sleep(1)  # 避免端口冲突
    
    print("=" * 50)
    print(f"📊 启动结果: {success_count}/{total_count} 服务成功启动")
    
    if success_count == total_count:
        print("🎉 所有服务启动成功!")
        print("\n📋 服务列表:")
        for service in MCP_SERVICES:
            print(f"  • {service['name']}: http://localhost:{service['port']}")
        
        print("\n🌐 管理界面: http://localhost:5173")
        print("🧪 集成测试: python3 /home/ubuntu/aicore0615/mcp/workflow/integration_test_framework.py")
    else:
        print("⚠️  部分服务启动失败，请检查日志")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

