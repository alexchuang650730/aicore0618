#!/usr/bin/env python3
"""
PowerAutomation 统一测试框架命令行接口
"""

import asyncio
import argparse
import sys
import json
from pathlib import Path
from datetime import datetime

# 添加项目路径
project_root = Path("/opt/powerautomation")
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "test"))

from framework import TestManager

class TestCLI:
    """测试框架命令行接口"""
    
    def __init__(self):
        self.test_manager = None
    
    async def init_manager(self):
        """初始化测试管理器"""
        if self.test_manager is None:
            self.test_manager = TestManager()
    
    async def run_command(self, args):
        """运行测试命令"""
        await self.init_manager()
        
        if args.all:
            session = await self.test_manager.run_all_tests(parallel=not args.sequential)
        elif args.module:
            session = await self.test_manager.run_module_tests(args.module, parallel=not args.sequential)
        elif args.type:
            if args.type == 'smoke':
                session = await self.test_manager.run_smoke_tests(parallel=not args.sequential)
            elif args.type == 'comprehensive':
                session = await self.test_manager.run_comprehensive_tests(parallel=not args.sequential)
            else:
                session = await self.test_manager.run_tests(test_type_filter=args.type, parallel=not args.sequential)
        else:
            session = await self.test_manager.run_all_tests(parallel=not args.sequential)
        
        # 输出结果
        self._print_session_results(session)
        
        return session.failed_tests == 0 and session.error_tests == 0
    
    async def discover_command(self, args):
        """发现测试命令"""
        await self.init_manager()
        
        tests = await self.test_manager.discover_tests(
            module_filter=args.module,
            test_type_filter=args.type
        )
        
        print(f"发现 {len(tests)} 个测试:")
        for test in tests:
            print(f"  - {test['test_id']} ({test['module_name']}, {test['test_type']})")
        
        return True
    
    async def status_command(self, args):
        """状态查询命令"""
        await self.init_manager()
        
        status = self.test_manager.get_status()
        
        print("PowerAutomation 测试框架状态:")
        print(f"  运行状态: {'运行中' if status['is_running'] else '空闲'}")
        print(f"  调度状态: {'已启动' if status['is_scheduled'] else '未启动'}")
        print(f"  总会话数: {status['total_sessions']}")
        
        if status['current_session']:
            print(f"  当前会话: {status['current_session']['session_id']}")
        
        if status['last_session']:
            last = status['last_session']
            print(f"  最后会话: {last['session_id']}")
            print(f"    - 测试数: {last['total_tests']}")
            print(f"    - 通过: {last['passed_tests']}")
            print(f"    - 失败: {last['failed_tests']}")
        
        return True
    
    async def schedule_command(self, args):
        """调度管理命令"""
        await self.init_manager()
        
        if args.start:
            await self.test_manager.start_scheduler()
            print("测试调度器已启动")
        elif args.stop:
            await self.test_manager.stop_scheduler()
            print("测试调度器已停止")
        elif args.status:
            scheduler_status = self.test_manager.scheduler.get_status()
            print("调度器状态:")
            print(f"  运行状态: {'运行中' if scheduler_status['is_running'] else '停止'}")
            print(f"  总任务数: {scheduler_status['total_tasks']}")
            print(f"  启用任务数: {scheduler_status['enabled_tasks']}")
            
            if scheduler_status['tasks']:
                print("  调度任务:")
                for task in scheduler_status['tasks']:
                    status_text = "启用" if task['enabled'] else "禁用"
                    print(f"    - {task['name']} ({task['cron_expr']}) [{status_text}]")
        elif args.list:
            next_runs = self.test_manager.scheduler.get_next_runs(hours=24)
            print(f"未来24小时内的调度计划 ({len(next_runs)} 个):")
            for run in next_runs:
                print(f"  - {run['scheduled_time']}: {run['name']}")
        
        return True
    
    async def report_command(self, args):
        """报告管理命令"""
        await self.init_manager()
        
        if args.generate:
            if args.type == 'daily':
                files = await self.test_manager.reporter.generate_daily_report()
            elif args.type == 'weekly':
                files = await self.test_manager.reporter.generate_weekly_report()
            elif args.type == 'monthly':
                files = await self.test_manager.reporter.generate_monthly_report()
            else:
                print(f"不支持的报告类型: {args.type}")
                return False
            
            print(f"生成了 {args.type} 报告:")
            for format_type, file_path in files.items():
                print(f"  - {format_type.upper()}: {file_path}")
        
        elif args.list:
            reports = self.test_manager.reporter.list_reports(
                report_type=args.type,
                limit=args.limit
            )
            
            print(f"报告列表 ({len(reports)} 个):")
            for report in reports:
                print(f"  - {report['file_name']} ({report['report_type']}) - {report['modified_time']}")
        
        elif args.cleanup:
            cleaned = await self.test_manager.reporter.cleanup_old_reports()
            print(f"清理了 {cleaned} 个旧报告文件")
        
        return True
    
    async def stats_command(self, args):
        """统计信息命令"""
        await self.init_manager()
        
        # 测试统计
        test_stats = self.test_manager.discovery.get_test_statistics()
        print("测试统计信息:")
        print(f"  总测试数: {test_stats['total_tests']}")
        print(f"  异步测试: {test_stats['async_tests']}")
        print(f"  预估总时间: {test_stats['total_estimated_duration']:.1f}秒")
        
        print("\n按模块分布:")
        for module, count in test_stats['by_module'].items():
            print(f"  - {module}: {count}")
        
        print("\n按类型分布:")
        for test_type, count in test_stats['by_type'].items():
            print(f"  - {test_type}: {count}")
        
        # 执行统计
        exec_stats = self.test_manager.get_test_statistics(days=args.days)
        print(f"\n过去{args.days}天执行统计:")
        print(f"  总会话数: {exec_stats['total_sessions']}")
        print(f"  总测试数: {exec_stats['total_tests']}")
        print(f"  平均成功率: {exec_stats['average_success_rate']*100:.1f}%")
        print(f"  趋势: {exec_stats['trend']}")
        
        return True
    
    def _print_session_results(self, session):
        """打印会话结果"""
        print(f"\n{'='*60}")
        print("测试执行结果")
        print(f"{'='*60}")
        print(f"会话ID: {session.session_id}")
        print(f"开始时间: {session.start_time}")
        print(f"结束时间: {session.end_time}")
        print(f"总测试数: {session.total_tests}")
        print(f"通过: {session.passed_tests}")
        print(f"失败: {session.failed_tests}")
        print(f"错误: {session.error_tests}")
        print(f"跳过: {session.skipped_tests}")
        
        if session.total_tests > 0:
            success_rate = session.passed_tests / session.total_tests * 100
            print(f"成功率: {success_rate:.1f}%")
        
        if session.end_time:
            duration = (session.end_time - session.start_time).total_seconds()
            print(f"执行时间: {duration:.2f}秒")
        
        # 显示失败的测试
        if session.failed_tests > 0 or session.error_tests > 0:
            print(f"\n失败/错误的测试:")
            for result in session.results:
                if result.status in ['FAIL', 'ERROR']:
                    print(f"  - {result.test_name} ({result.status})")
                    if result.error_message:
                        print(f"    错误: {result.error_message}")
        
        print(f"{'='*60}")

async def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='PowerAutomation 统一测试框架')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # run 命令
    run_parser = subparsers.add_parser('run', help='运行测试')
    run_parser.add_argument('--all', action='store_true', help='运行所有测试')
    run_parser.add_argument('--module', help='运行指定模块的测试')
    run_parser.add_argument('--type', choices=['unit', 'integration', 'comprehensive', 'simple', 'smoke'], help='运行指定类型的测试')
    run_parser.add_argument('--sequential', action='store_true', help='串行执行测试')
    
    # discover 命令
    discover_parser = subparsers.add_parser('discover', help='发现测试')
    discover_parser.add_argument('--module', help='过滤模块')
    discover_parser.add_argument('--type', help='过滤类型')
    
    # status 命令
    subparsers.add_parser('status', help='查看状态')
    
    # schedule 命令
    schedule_parser = subparsers.add_parser('schedule', help='调度管理')
    schedule_parser.add_argument('--start', action='store_true', help='启动调度器')
    schedule_parser.add_argument('--stop', action='store_true', help='停止调度器')
    schedule_parser.add_argument('--status', action='store_true', help='查看调度器状态')
    schedule_parser.add_argument('--list', action='store_true', help='列出调度计划')
    
    # report 命令
    report_parser = subparsers.add_parser('report', help='报告管理')
    report_parser.add_argument('--generate', action='store_true', help='生成报告')
    report_parser.add_argument('--list', action='store_true', help='列出报告')
    report_parser.add_argument('--cleanup', action='store_true', help='清理旧报告')
    report_parser.add_argument('--type', choices=['daily', 'weekly', 'monthly'], help='报告类型')
    report_parser.add_argument('--limit', type=int, default=10, help='列表限制数量')
    
    # stats 命令
    stats_parser = subparsers.add_parser('stats', help='统计信息')
    stats_parser.add_argument('--days', type=int, default=7, help='统计天数')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = TestCLI()
    
    try:
        if args.command == 'run':
            success = await cli.run_command(args)
        elif args.command == 'discover':
            success = await cli.discover_command(args)
        elif args.command == 'status':
            success = await cli.status_command(args)
        elif args.command == 'schedule':
            success = await cli.schedule_command(args)
        elif args.command == 'report':
            success = await cli.report_command(args)
        elif args.command == 'stats':
            success = await cli.stats_command(args)
        else:
            print(f"未知命令: {args.command}")
            success = False
        
        # 清理资源
        if cli.test_manager:
            await cli.test_manager.cleanup()
        
        sys.exit(0 if success else 1)
        
    except Exception as e:
        print(f"命令执行失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

