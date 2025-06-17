#!/usr/bin/env python3
"""
PowerAutomation 测试运行器
负责执行测试并收集结果
"""

import asyncio
import logging
import subprocess
import sys
import time
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import concurrent.futures
import json
import tempfile

class TestRunner:
    """
    PowerAutomation 测试运行器
    
    功能:
    - 执行单个和批量测试
    - 并行测试执行
    - 测试结果收集
    - 超时和错误处理
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.project_root = Path("/opt/powerautomation")
        
        # 设置日志
        self.logger = logging.getLogger(__name__)
        
        # 测试配置
        self.timeout = config.get('test_settings', {}).get('timeout', 300)
        self.retry_count = config.get('test_settings', {}).get('retry_count', 3)
        self.fail_fast = config.get('test_settings', {}).get('fail_fast', False)
        
        self.logger.info("TestRunner initialized")
    
    async def run_tests(self,
                       tests: List[Dict[str, Any]],
                       parallel: bool = True,
                       max_workers: int = 4) -> List[Dict[str, Any]]:
        """
        运行测试列表
        
        Args:
            tests: 测试列表
            parallel: 是否并行执行
            max_workers: 最大并行数
        
        Returns:
            测试结果列表
        """
        if not tests:
            self.logger.warning("No tests to run")
            return []
        
        self.logger.info(f"Running {len(tests)} tests (parallel: {parallel}, workers: {max_workers})")
        
        start_time = time.time()
        results = []
        
        if parallel and len(tests) > 1:
            # 并行执行
            results = await self._run_tests_parallel(tests, max_workers)
        else:
            # 串行执行
            results = await self._run_tests_sequential(tests)
        
        end_time = time.time()
        total_duration = end_time - start_time
        
        self.logger.info(f"Completed {len(tests)} tests in {total_duration:.2f}s")
        
        # 统计结果
        passed = sum(1 for r in results if r.get('status') == 'PASS')
        failed = sum(1 for r in results if r.get('status') == 'FAIL')
        errors = sum(1 for r in results if r.get('status') == 'ERROR')
        
        self.logger.info(f"Results: {passed} passed, {failed} failed, {errors} errors")
        
        return results
    
    async def _run_tests_parallel(self, tests: List[Dict[str, Any]], max_workers: int) -> List[Dict[str, Any]]:
        """并行运行测试"""
        self.logger.info(f"Running tests in parallel with {max_workers} workers")
        
        # 使用线程池执行器
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 创建任务
            loop = asyncio.get_event_loop()
            tasks = []
            
            for test in tests:
                task = loop.run_in_executor(
                    executor,
                    self._run_single_test_sync,
                    test
                )
                tasks.append(task)
            
            # 等待所有任务完成
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 处理异常结果
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    self.logger.error(f"Test execution failed: {result}")
                    processed_results.append(self._create_error_result(tests[i], str(result)))
                else:
                    processed_results.append(result)
            
            return processed_results
    
    async def _run_tests_sequential(self, tests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """串行运行测试"""
        self.logger.info("Running tests sequentially")
        
        results = []
        
        for i, test in enumerate(tests, 1):
            self.logger.info(f"Running test {i}/{len(tests)}: {test['test_name']}")
            
            try:
                result = await self._run_single_test(test)
                results.append(result)
                
                # 如果启用了fail_fast且测试失败，则停止执行
                if self.fail_fast and result.get('status') in ['FAIL', 'ERROR']:
                    self.logger.warning(f"Stopping execution due to fail_fast mode (test failed: {test['test_name']})")
                    break
                    
            except Exception as e:
                self.logger.error(f"Test execution failed: {e}")
                results.append(self._create_error_result(test, str(e)))
                
                if self.fail_fast:
                    break
        
        return results
    
    async def _run_single_test(self, test: Dict[str, Any]) -> Dict[str, Any]:
        """运行单个测试（异步版本）"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._run_single_test_sync, test)
    
    def _run_single_test_sync(self, test: Dict[str, Any]) -> Dict[str, Any]:
        """运行单个测试（同步版本）"""
        test_id = test['test_id']
        test_name = test['test_name']
        file_path = test['file_path']
        
        self.logger.debug(f"Executing test: {test_id}")
        
        start_time = datetime.now()
        
        try:
            # 构建测试命令
            if test.get('test_class'):
                # 类方法测试
                test_target = f"{Path(file_path).stem}.{test['test_class']}.{test['test_function']}"
            else:
                # 函数测试
                test_target = f"{Path(file_path).stem}.{test['test_function']}"
            
            # 执行测试
            result = self._execute_test_command(file_path, test_target, test)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            # 创建结果
            test_result = {
                'test_id': test_id,
                'test_name': test_name,
                'module_name': test['module_name'],
                'test_type': test['test_type'],
                'status': result['status'],
                'duration': duration,
                'start_time': start_time,
                'end_time': end_time,
                'output': result.get('output', ''),
                'error_message': result.get('error_message'),
                'details': {
                    'file_path': file_path,
                    'test_class': test.get('test_class'),
                    'test_function': test['test_function'],
                    'command': result.get('command'),
                    'return_code': result.get('return_code'),
                    'retry_count': result.get('retry_count', 0)
                }
            }
            
            return test_result
            
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            self.logger.error(f"Test execution failed: {test_id}, error: {e}")
            
            return {
                'test_id': test_id,
                'test_name': test_name,
                'module_name': test['module_name'],
                'test_type': test['test_type'],
                'status': 'ERROR',
                'duration': duration,
                'start_time': start_time,
                'end_time': end_time,
                'error_message': str(e),
                'details': {
                    'file_path': file_path,
                    'exception_type': type(e).__name__
                }
            }
    
    def _execute_test_command(self, file_path: str, test_target: str, test_info: Dict[str, Any]) -> Dict[str, Any]:
        """执行测试命令"""
        file_path_obj = Path(file_path)
        test_dir = file_path_obj.parent
        
        # 构建命令
        if test_info.get('test_class'):
            # unittest格式
            cmd = [
                sys.executable, '-m', 'unittest',
                f"{file_path_obj.stem}.{test_info['test_class']}.{test_info['test_function']}",
                '-v'
            ]
        else:
            # 直接运行文件
            cmd = [sys.executable, file_path_obj.name]
        
        retry_count = 0
        last_error = None
        
        # 重试机制
        while retry_count <= self.retry_count:
            try:
                self.logger.debug(f"Executing command: {' '.join(cmd)} (attempt {retry_count + 1})")
                
                # 获取测试环境
                env = self._get_test_environment()
                
                # 确保工作目录在Python路径中
                env['PYTHONPATH'] = f"{test_dir}:{env.get('PYTHONPATH', '')}"
                
                # 执行命令
                process = subprocess.run(
                    cmd,
                    cwd=test_dir,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                    env=env
                )
                
                # 分析结果
                status = self._analyze_test_output(process.returncode, process.stdout, process.stderr)
                
                return {
                    'status': status,
                    'output': process.stdout,
                    'error_output': process.stderr,
                    'return_code': process.returncode,
                    'command': ' '.join(cmd),
                    'retry_count': retry_count
                }
                
            except subprocess.TimeoutExpired:
                last_error = f"Test timed out after {self.timeout}s"
                self.logger.warning(f"Test timed out: {test_target} (attempt {retry_count + 1})")
                
            except Exception as e:
                last_error = str(e)
                self.logger.warning(f"Test execution failed: {test_target} (attempt {retry_count + 1}), error: {e}")
            
            retry_count += 1
            
            # 如果不是最后一次重试，等待一下
            if retry_count <= self.retry_count:
                time.sleep(1)
        
        # 所有重试都失败了
        return {
            'status': 'ERROR',
            'error_message': last_error or "Test execution failed after all retries",
            'retry_count': retry_count - 1,
            'command': ' '.join(cmd)
        }

    def _get_test_environment(self) -> Dict[str, str]:
        """获取测试环境变量"""
        import os
        env = os.environ.copy()
        
        # 添加项目根目录到Python路径
        python_path = env.get('PYTHONPATH', '')
        project_paths = [
            str(self.project_root),
            str(self.project_root / 'mcp'),
            str(self.project_root / 'mcp' / 'adapter'),
            str(self.project_root / 'test'),
        ]
        
        for path in project_paths:
            if path not in python_path:
                python_path = f"{path}:{python_path}" if python_path else path
        
        env['PYTHONPATH'] = python_path
        
        # 设置测试环境标志
        env['POWERAUTOMATION_TEST_MODE'] = '1'
        env['POWERAUTOMATION_PROJECT_ROOT'] = str(self.project_root)
        
        return env
    
    def _analyze_test_output(self, return_code: int, stdout: str, stderr: str) -> str:
        """分析测试输出确定状态"""
        # 基于返回码
        if return_code == 0:
            # 进一步检查输出
            if 'OK' in stdout or 'passed' in stdout.lower():
                return 'PASS'
            elif 'FAILED' in stdout or 'failed' in stdout.lower():
                return 'FAIL'
            elif 'ERROR' in stdout or 'error' in stdout.lower():
                return 'ERROR'
            else:
                return 'PASS'  # 默认认为成功
        else:
            # 检查是否是测试失败还是错误
            if 'FAILED' in stdout or 'AssertionError' in stderr:
                return 'FAIL'
            else:
                return 'ERROR'
    
    def _create_error_result(self, test: Dict[str, Any], error_message: str) -> Dict[str, Any]:
        """创建错误结果"""
        return {
            'test_id': test['test_id'],
            'test_name': test['test_name'],
            'module_name': test['module_name'],
            'test_type': test['test_type'],
            'status': 'ERROR',
            'duration': 0.0,
            'start_time': datetime.now(),
            'end_time': datetime.now(),
            'error_message': error_message,
            'details': {
                'file_path': test['file_path'],
                'execution_error': True
            }
        }
    
    async def run_single_test_by_id(self, test_id: str) -> Optional[Dict[str, Any]]:
        """根据测试ID运行单个测试"""
        # 这里需要从测试发现器获取测试信息
        # 简化实现，实际应该集成测试发现器
        self.logger.warning(f"run_single_test_by_id not fully implemented for {test_id}")
        return None
    
    def get_runner_status(self) -> Dict[str, Any]:
        """获取运行器状态"""
        return {
            'timeout': self.timeout,
            'retry_count': self.retry_count,
            'fail_fast': self.fail_fast,
            'project_root': str(self.project_root)
        }
    
    async def cleanup(self):
        """清理资源"""
        self.logger.info("TestRunner cleanup completed")

