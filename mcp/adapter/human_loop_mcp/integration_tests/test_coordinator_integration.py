#!/usr/bin/env python3
"""
Human-in-the-Loop MCP 集成测试
测试与MCP Coordinator的通信和集成
"""

import sys
import os
import time
import json
import requests
import asyncio
from datetime import datetime

# 添加项目路径
sys.path.append('/home/ubuntu/aicore0615/mcp/adapter/human_loop_mcp/src')

def test_coordinator_connection():
    """测试与MCP Coordinator的连接"""
    print("🔗 测试MCP Coordinator连接...")
    
    try:
        response = requests.get("http://localhost:8089/health", timeout=5)
        if response.status_code == 200:
            print("✅ MCP Coordinator连接成功")
            return True
        else:
            print(f"❌ MCP Coordinator连接失败: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ MCP Coordinator连接异常: {e}")
        return False

def test_human_loop_mcp_health():
    """测试Human-in-the-Loop MCP健康状态"""
    print("🏥 测试Human-in-the-Loop MCP健康状态...")
    
    try:
        response = requests.get("http://localhost:8096/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Human-in-the-Loop MCP健康检查通过")
            print(f"   - 服务状态: {data.get('status')}")
            print(f"   - 协调器注册状态: {data.get('coordinator_registered')}")
            print(f"   - 活跃会话数: {data.get('active_sessions')}")
            return True
        else:
            print(f"❌ Human-in-the-Loop MCP健康检查失败: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Human-in-the-Loop MCP健康检查异常: {e}")
        return False

def test_mcp_registration():
    """测试MCP注册"""
    print("📝 测试MCP注册...")
    
    try:
        # 检查协调器状态
        response = requests.get("http://localhost:8096/api/coordinator/status", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ 协调器状态检查成功")
            print(f"   - 协调器连接: {data.get('coordinator_connected')}")
            print(f"   - 注册状态: {data.get('registered')}")
            
            if data.get('coordinator_info'):
                coordinator_info = data['coordinator_info']
                print(f"   - 协调器ID: {coordinator_info.get('coordinator_id')}")
                print(f"   - 协调器版本: {coordinator_info.get('version')}")
                print(f"   - 已注册MCP数量: {coordinator_info.get('registered_mcps')}")
            
            return data.get('registered', False)
        else:
            print(f"❌ 协调器状态检查失败: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 协调器状态检查异常: {e}")
        return False

def test_mcp_list():
    """测试获取MCP列表"""
    print("📋 测试获取MCP列表...")
    
    try:
        response = requests.get("http://localhost:8096/api/mcp/list", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ 获取MCP列表成功")
            print(f"   - 已注册MCP总数: {data.get('total', 0)}")
            
            registered_mcps = data.get('registered_mcps', {})
            for mcp_id, mcp_info in registered_mcps.items():
                print(f"   - {mcp_id}: {mcp_info.get('status', 'unknown')}")
            
            return True
        else:
            print(f"❌ 获取MCP列表失败: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 获取MCP列表异常: {e}")
        return False

def test_session_creation():
    """测试会话创建"""
    print("🆕 测试会话创建...")
    
    try:
        session_data = {
            "interaction_type": "confirmation",
            "title": "测试确认对话框",
            "message": "这是一个测试确认对话框，请选择确认或取消。",
            "fields": [
                {
                    "type": "button",
                    "name": "action",
                    "label": "操作",
                    "options": [
                        {"label": "确认", "value": "confirm"},
                        {"label": "取消", "value": "cancel"}
                    ]
                }
            ],
            "timeout": 300
        }
        
        response = requests.post(
            "http://localhost:8096/api/sessions",
            json=session_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            session_id = data.get('session_id')
            print("✅ 会话创建成功")
            print(f"   - 会话ID: {session_id}")
            print(f"   - 状态: {data.get('status')}")
            print(f"   - 创建时间: {data.get('created_at')}")
            return session_id
        else:
            print(f"❌ 会话创建失败: HTTP {response.status_code}")
            print(f"   - 响应: {response.text}")
            return None
    except Exception as e:
        print(f"❌ 会话创建异常: {e}")
        return None

def test_session_query(session_id):
    """测试会话查询"""
    if not session_id:
        print("⏭️ 跳过会话查询测试（无有效会话ID）")
        return False
    
    print("🔍 测试会话查询...")
    
    try:
        response = requests.get(f"http://localhost:8096/api/sessions/{session_id}", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ 会话查询成功")
            print(f"   - 会话ID: {data.get('session_id')}")
            print(f"   - 状态: {data.get('status')}")
            print(f"   - 交互类型: {data.get('interaction_data', {}).get('interaction_type')}")
            return True
        else:
            print(f"❌ 会话查询失败: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 会话查询异常: {e}")
        return False

def test_mcp_communication():
    """测试MCP间通信"""
    print("🔄 测试MCP间通信...")
    
    try:
        # 尝试调用一个不存在的MCP来测试错误处理
        test_data = {
            "action": "test_action",
            "params": {
                "message": "这是一个测试消息"
            }
        }
        
        response = requests.post(
            "http://localhost:8096/api/mcp/call/test_mcp",
            json=test_data,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ MCP通信接口正常")
            if data.get('success'):
                print("   - 通信成功")
            else:
                print(f"   - 通信失败（预期）: {data.get('error')}")
            return True
        else:
            print(f"❌ MCP通信接口失败: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ MCP通信接口异常: {e}")
        return False

def test_statistics():
    """测试统计信息"""
    print("📊 测试统计信息...")
    
    try:
        response = requests.get("http://localhost:8096/api/statistics", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ 统计信息获取成功")
            print(f"   - 总会话数: {data.get('total_sessions', 0)}")
            print(f"   - 活跃会话数: {data.get('active_sessions', 0)}")
            print(f"   - 完成会话数: {data.get('completed_sessions', 0)}")
            return True
        else:
            print(f"❌ 统计信息获取失败: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 统计信息获取异常: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 Human-in-the-Loop MCP 集成测试")
    print("=" * 60)
    
    test_results = []
    
    # 测试1: MCP Coordinator连接
    test_results.append(("Coordinator连接", test_coordinator_connection()))
    
    # 测试2: Human-in-the-Loop MCP健康状态
    test_results.append(("MCP健康状态", test_human_loop_mcp_health()))
    
    # 测试3: MCP注册
    test_results.append(("MCP注册", test_mcp_registration()))
    
    # 测试4: MCP列表
    test_results.append(("MCP列表", test_mcp_list()))
    
    # 测试5: 会话创建
    session_id = test_session_creation()
    test_results.append(("会话创建", session_id is not None))
    
    # 测试6: 会话查询
    test_results.append(("会话查询", test_session_query(session_id)))
    
    # 测试7: MCP间通信
    test_results.append(("MCP间通信", test_mcp_communication()))
    
    # 测试8: 统计信息
    test_results.append(("统计信息", test_statistics()))
    
    # 输出测试结果
    print("\n" + "=" * 60)
    print("📋 测试结果汇总")
    print("=" * 60)
    
    passed = 0
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:<20} {status}")
        if result:
            passed += 1
    
    print("=" * 60)
    print(f"总测试数: {total}")
    print(f"通过数量: {passed}")
    print(f"失败数量: {total - passed}")
    print(f"通过率: {passed/total*100:.1f}%")
    
    if passed == total:
        print("\n🎉 所有测试通过！Human-in-the-Loop MCP集成成功！")
        return True
    else:
        print(f"\n⚠️ 有 {total - passed} 个测试失败，请检查配置和服务状态。")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

