#!/usr/bin/env python3
"""
PowerAutomation 统一测试框架主入口
"""

import asyncio
import sys
import logging
from pathlib import Path

# 添加项目路径
project_root = Path("/opt/powerautomation")
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "test"))

from framework import TestManager

async def main():
    """主函数"""
    # 设置基本日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger = logging.getLogger(__name__)
    logger.info("Starting PowerAutomation Unified Test Framework")
    
    try:
        # 创建测试管理器
        test_manager = TestManager()
        
        # 运行所有测试
        session = await test_manager.run_all_tests()
        
        # 输出结果
        print(f"\n{'='*60}")
        print("PowerAutomation 统一测试框架执行完成")
        print(f"{'='*60}")
        print(f"会话ID: {session.session_id}")
        print(f"总测试数: {session.total_tests}")
        print(f"通过: {session.passed_tests}")
        print(f"失败: {session.failed_tests}")
        print(f"错误: {session.error_tests}")
        print(f"跳过: {session.skipped_tests}")
        print(f"成功率: {session.passed_tests/session.total_tests*100:.1f}%" if session.total_tests > 0 else "成功率: 0%")
        print(f"执行时间: {(session.end_time - session.start_time).total_seconds():.2f}秒")
        print(f"{'='*60}")
        
        # 清理资源
        await test_manager.cleanup()
        
        # 返回适当的退出码
        if session.failed_tests > 0 or session.error_tests > 0:
            sys.exit(1)
        else:
            sys.exit(0)
            
    except Exception as e:
        logger.error(f"Test framework execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

