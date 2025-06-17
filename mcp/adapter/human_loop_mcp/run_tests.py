#!/usr/bin/env python3
"""
Human-in-the-Loop MCP 测试运行器
统一运行所有测试用例
"""

import os
import sys
import unittest
import argparse
import time
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

def run_unit_tests():
    """运行单元测试"""
    print("=" * 60)
    print("运行单元测试...")
    print("=" * 60)
    
    # 发现并运行单元测试
    test_dir = Path(__file__).parent.parent / 'unit_tests'
    loader = unittest.TestLoader()
    suite = loader.discover(str(test_dir), pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def run_integration_tests():
    """运行集成测试"""
    print("\n" + "=" * 60)
    print("运行集成测试...")
    print("=" * 60)
    
    # 发现并运行集成测试
    test_dir = Path(__file__).parent.parent / 'integration_tests'
    loader = unittest.TestLoader()
    suite = loader.discover(str(test_dir), pattern='test_*.py')
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()

def run_performance_tests():
    """运行性能测试"""
    print("\n" + "=" * 60)
    print("运行性能测试...")
    print("=" * 60)
    
    try:
        import requests
        import threading
        import time
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        base_url = "http://127.0.0.1:8097"
        
        def create_session():
            """创建测试会话"""
            session_data = {
                "interaction_data": {
                    "interaction_type": "confirmation",
                    "title": "性能测试",
                    "message": "这是一个性能测试会话",
                    "timeout": 60
                },
                "workflow_id": "performance-test"
            }
            
            try:
                response = requests.post(
                    f"{base_url}/api/sessions",
                    json=session_data,
                    timeout=5
                )
                return response.status_code == 200
            except:
                return False
        
        def respond_to_session(session_id):
            """响应会话"""
            try:
                response = requests.post(
                    f"{base_url}/api/sessions/{session_id}/respond",
                    json={
                        "response": {"choice": "yes"},
                        "user_id": "perf-test-user"
                    },
                    timeout=5
                )
                return response.status_code == 200
            except:
                return False
        
        # 测试并发会话创建
        print("测试并发会话创建...")
        concurrent_sessions = 10
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=concurrent_sessions) as executor:
            futures = [executor.submit(create_session) for _ in range(concurrent_sessions)]
            results = [future.result() for future in as_completed(futures)]
        
        end_time = time.time()
        success_count = sum(results)
        
        print(f"创建 {concurrent_sessions} 个会话:")
        print(f"  成功: {success_count}")
        print(f"  失败: {concurrent_sessions - success_count}")
        print(f"  耗时: {end_time - start_time:.2f} 秒")
        print(f"  平均响应时间: {(end_time - start_time) / concurrent_sessions:.3f} 秒")
        
        # 测试API响应时间
        print("\n测试API响应时间...")
        api_tests = [
            ("健康检查", f"{base_url}/api/health"),
            ("获取统计", f"{base_url}/api/statistics"),
            ("获取模板", f"{base_url}/api/templates"),
            ("获取会话列表", f"{base_url}/api/sessions")
        ]
        
        for test_name, url in api_tests:
            try:
                start_time = time.time()
                response = requests.get(url, timeout=5)
                end_time = time.time()
                
                print(f"  {test_name}: {end_time - start_time:.3f} 秒 (状态码: {response.status_code})")
            except Exception as e:
                print(f"  {test_name}: 失败 - {e}")
        
        return True
        
    except ImportError:
        print("跳过性能测试 - 缺少 requests 库")
        return True
    except Exception as e:
        print(f"性能测试失败: {e}")
        return False

def run_all_tests():
    """运行所有测试"""
    print("Human-in-the-Loop MCP 测试套件")
    print("=" * 60)
    
    results = []
    
    # 运行单元测试
    unit_success = run_unit_tests()
    results.append(("单元测试", unit_success))
    
    # 运行集成测试
    integration_success = run_integration_tests()
    results.append(("集成测试", integration_success))
    
    # 运行性能测试
    performance_success = run_performance_tests()
    results.append(("性能测试", performance_success))
    
    # 输出总结
    print("\n" + "=" * 60)
    print("测试结果总结:")
    print("=" * 60)
    
    all_passed = True
    for test_type, success in results:
        status = "通过" if success else "失败"
        print(f"  {test_type}: {status}")
        if not success:
            all_passed = False
    
    print("=" * 60)
    if all_passed:
        print("所有测试通过! ✅")
        return 0
    else:
        print("部分测试失败! ❌")
        return 1

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='Human-in-the-Loop MCP 测试运行器')
    parser.add_argument('--unit', action='store_true', help='只运行单元测试')
    parser.add_argument('--integration', action='store_true', help='只运行集成测试')
    parser.add_argument('--performance', action='store_true', help='只运行性能测试')
    parser.add_argument('--all', action='store_true', help='运行所有测试 (默认)')
    
    args = parser.parse_args()
    
    # 如果没有指定特定测试类型，默认运行所有测试
    if not any([args.unit, args.integration, args.performance]):
        args.all = True
    
    exit_code = 0
    
    try:
        if args.all:
            exit_code = run_all_tests()
        else:
            if args.unit:
                success = run_unit_tests()
                if not success:
                    exit_code = 1
            
            if args.integration:
                success = run_integration_tests()
                if not success:
                    exit_code = 1
            
            if args.performance:
                success = run_performance_tests()
                if not success:
                    exit_code = 1
    
    except KeyboardInterrupt:
        print("\n测试被用户中断")
        exit_code = 130
    except Exception as e:
        print(f"\n测试运行器异常: {e}")
        exit_code = 1
    
    sys.exit(exit_code)

if __name__ == '__main__':
    main()

