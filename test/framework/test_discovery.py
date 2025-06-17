#!/usr/bin/env python3
"""
PowerAutomation 测试发现器
负责自动发现和分类测试
"""

import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
import re
import ast
import importlib.util

class TestDiscovery:
    """
    PowerAutomation 测试发现器
    
    功能:
    - 自动发现测试文件
    - 分析测试内容
    - 分类测试类型
    - 提取测试元数据
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.project_root = Path("/opt/powerautomation")
        self.mcp_root = self.project_root / "mcp"
        
        # 设置日志
        self.logger = logging.getLogger(__name__)
        
        # 测试发现配置
        self.include_patterns = config.get('test_discovery', {}).get('include_patterns', [
            "*/unit_tests/test_*.py",
            "*/integration_tests/test_*.py"
        ])
        
        self.exclude_patterns = config.get('test_discovery', {}).get('exclude_patterns', [
            "*/__pycache__/*",
            "*/.*",
            "*/*_backup/*"
        ])
        
        self.logger.info("TestDiscovery initialized")
    
    async def discover_tests(self,
                           module_filter: Optional[str] = None,
                           test_type_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        发现测试
        
        Args:
            module_filter: 模块过滤器 (如 'cloud_search_mcp')
            test_type_filter: 测试类型过滤器 (unit, integration, comprehensive, simple)
        
        Returns:
            测试列表
        """
        self.logger.info(f"Discovering tests with filters: module={module_filter}, type={test_type_filter}")
        
        # 发现所有测试文件
        test_files = self._find_test_files()
        
        # 分析测试文件
        tests = []
        for test_file in test_files:
            try:
                test_info = await self._analyze_test_file(test_file)
                if test_info:
                    tests.extend(test_info)
            except Exception as e:
                self.logger.warning(f"Failed to analyze test file {test_file}: {e}")
        
        # 应用过滤器
        filtered_tests = self._apply_filters(tests, module_filter, test_type_filter)
        
        self.logger.info(f"Discovered {len(filtered_tests)} tests (from {len(test_files)} files)")
        return filtered_tests
    
    def _find_test_files(self) -> List[Path]:
        """查找测试文件"""
        test_files = []
        
        # 使用include模式查找文件
        for pattern in self.include_patterns:
            found_files = list(self.mcp_root.glob(pattern))
            test_files.extend(found_files)
        
        # 应用exclude模式
        filtered_files = []
        for test_file in test_files:
            should_exclude = False
            for exclude_pattern in self.exclude_patterns:
                if test_file.match(exclude_pattern):
                    should_exclude = True
                    break
            
            if not should_exclude:
                filtered_files.append(test_file)
        
        # 去重并排序
        unique_files = list(set(filtered_files))
        unique_files.sort()
        
        self.logger.debug(f"Found {len(unique_files)} test files")
        return unique_files
    
    async def _analyze_test_file(self, test_file: Path) -> List[Dict[str, Any]]:
        """分析测试文件"""
        try:
            # 读取文件内容
            content = test_file.read_text(encoding='utf-8')
            
            # 解析AST
            tree = ast.parse(content)
            
            # 提取测试信息
            tests = []
            
            # 分析模块级信息
            module_info = self._extract_module_info(test_file, content)
            
            # 查找测试类和方法
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and self._is_test_class(node.name):
                    class_tests = self._analyze_test_class(node, test_file, module_info)
                    tests.extend(class_tests)
                elif isinstance(node, ast.FunctionDef) and self._is_test_function(node.name):
                    function_test = self._analyze_test_function(node, test_file, module_info)
                    if function_test:
                        tests.append(function_test)
            
            return tests
            
        except Exception as e:
            self.logger.error(f"Error analyzing test file {test_file}: {e}")
            return []
    
    def _extract_module_info(self, test_file: Path, content: str) -> Dict[str, Any]:
        """提取模块信息"""
        # 从路径推断模块信息
        parts = test_file.parts
        
        # 查找MCP模块名
        module_name = None
        test_type = None
        
        for i, part in enumerate(parts):
            if part.endswith('_mcp'):
                module_name = part
                break
        
        # 确定测试类型
        if 'unit_tests' in parts:
            test_type = 'unit'
        elif 'integration_tests' in parts:
            test_type = 'integration'
        
        # 从文件名推断更具体的类型
        file_name = test_file.stem
        if 'comprehensive' in file_name:
            test_subtype = 'comprehensive'
        elif 'simple' in file_name:
            test_subtype = 'simple'
        elif 'performance' in file_name:
            test_subtype = 'performance'
        else:
            test_subtype = 'standard'
        
        # 提取文档字符串
        docstring = self._extract_module_docstring(content)
        
        return {
            'module_name': module_name,
            'test_type': test_type,
            'test_subtype': test_subtype,
            'file_path': str(test_file),
            'file_name': test_file.name,
            'docstring': docstring
        }
    
    def _extract_module_docstring(self, content: str) -> Optional[str]:
        """提取模块文档字符串"""
        try:
            tree = ast.parse(content)
            if (tree.body and 
                isinstance(tree.body[0], ast.Expr) and 
                isinstance(tree.body[0].value, ast.Constant) and 
                isinstance(tree.body[0].value.value, str)):
                return tree.body[0].value.value.strip()
        except:
            pass
        return None
    
    def _is_test_class(self, class_name: str) -> bool:
        """判断是否为测试类"""
        return (class_name.startswith('Test') or 
                class_name.endswith('Test') or
                'Test' in class_name)
    
    def _is_test_function(self, func_name: str) -> bool:
        """判断是否为测试函数"""
        return func_name.startswith('test_')
    
    def _analyze_test_class(self, class_node: ast.ClassDef, test_file: Path, module_info: Dict[str, Any]) -> List[Dict[str, Any]]:
        """分析测试类"""
        tests = []
        
        # 提取类文档字符串
        class_docstring = ast.get_docstring(class_node)
        
        # 查找测试方法
        for node in class_node.body:
            if isinstance(node, ast.FunctionDef) and self._is_test_function(node.name):
                test_info = self._create_test_info(
                    test_id=f"{module_info['module_name']}.{class_node.name}.{node.name}",
                    test_name=node.name,
                    test_class=class_node.name,
                    test_function=node.name,
                    test_file=test_file,
                    module_info=module_info,
                    docstring=ast.get_docstring(node) or class_docstring
                )
                tests.append(test_info)
        
        return tests
    
    def _analyze_test_function(self, func_node: ast.FunctionDef, test_file: Path, module_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """分析测试函数"""
        return self._create_test_info(
            test_id=f"{module_info['module_name']}.{func_node.name}",
            test_name=func_node.name,
            test_class=None,
            test_function=func_node.name,
            test_file=test_file,
            module_info=module_info,
            docstring=ast.get_docstring(func_node)
        )
    
    def _create_test_info(self,
                         test_id: str,
                         test_name: str,
                         test_class: Optional[str],
                         test_function: str,
                         test_file: Path,
                         module_info: Dict[str, Any],
                         docstring: Optional[str]) -> Dict[str, Any]:
        """创建测试信息"""
        # 判断是否为异步测试
        is_async = self._is_async_test(test_file, test_function)
        
        # 估算测试复杂度
        complexity = self._estimate_test_complexity(test_file, test_function)
        
        # 提取标签
        tags = self._extract_test_tags(docstring, test_name)
        
        return {
            'test_id': test_id,
            'test_name': test_name,
            'test_class': test_class,
            'test_function': test_function,
            'module_name': module_info['module_name'],
            'test_type': module_info['test_type'],
            'test_subtype': module_info['test_subtype'],
            'file_path': str(test_file),
            'file_name': test_file.name,
            'is_async': is_async,
            'complexity': complexity,
            'tags': tags,
            'docstring': docstring,
            'estimated_duration': self._estimate_duration(complexity, is_async),
            'dependencies': self._extract_dependencies(test_file),
            'metadata': {
                'discovered_at': asyncio.get_event_loop().time(),
                'file_size': test_file.stat().st_size,
                'last_modified': test_file.stat().st_mtime
            }
        }
    
    def _is_async_test(self, test_file: Path, test_function: str) -> bool:
        """判断是否为异步测试"""
        try:
            content = test_file.read_text(encoding='utf-8')
            # 简单的正则匹配
            pattern = rf'async\s+def\s+{re.escape(test_function)}\s*\('
            return bool(re.search(pattern, content))
        except:
            return False
    
    def _estimate_test_complexity(self, test_file: Path, test_function: str) -> str:
        """估算测试复杂度"""
        try:
            content = test_file.read_text(encoding='utf-8')
            
            # 查找函数内容
            lines = content.split('\n')
            in_function = False
            function_lines = []
            indent_level = None
            
            for line in lines:
                if f'def {test_function}(' in line:
                    in_function = True
                    indent_level = len(line) - len(line.lstrip())
                    continue
                
                if in_function:
                    current_indent = len(line) - len(line.lstrip())
                    if line.strip() and current_indent <= indent_level:
                        break
                    function_lines.append(line)
            
            # 基于行数和关键词判断复杂度
            line_count = len([line for line in function_lines if line.strip()])
            
            # 计算关键词权重
            complexity_keywords = {
                'await': 2,
                'asyncio': 2,
                'mock': 1,
                'patch': 1,
                'assert': 1,
                'for': 2,
                'while': 2,
                'if': 1,
                'try': 2,
                'except': 2
            }
            
            keyword_score = 0
            function_content = '\n'.join(function_lines).lower()
            for keyword, weight in complexity_keywords.items():
                keyword_score += function_content.count(keyword) * weight
            
            # 综合评分
            total_score = line_count + keyword_score
            
            if total_score < 10:
                return 'simple'
            elif total_score < 25:
                return 'medium'
            else:
                return 'complex'
                
        except:
            return 'unknown'
    
    def _extract_test_tags(self, docstring: Optional[str], test_name: str) -> List[str]:
        """提取测试标签"""
        tags = []
        
        # 从测试名称推断标签
        if 'smoke' in test_name.lower():
            tags.append('smoke')
        if 'integration' in test_name.lower():
            tags.append('integration')
        if 'performance' in test_name.lower():
            tags.append('performance')
        if 'async' in test_name.lower():
            tags.append('async')
        if 'error' in test_name.lower() or 'exception' in test_name.lower():
            tags.append('error_handling')
        
        # 从文档字符串提取标签
        if docstring:
            # 查找 @tag 标记
            tag_pattern = r'@tag\s+(\w+)'
            found_tags = re.findall(tag_pattern, docstring, re.IGNORECASE)
            tags.extend(found_tags)
            
            # 查找常见关键词
            if 'slow' in docstring.lower():
                tags.append('slow')
            if 'flaky' in docstring.lower():
                tags.append('flaky')
            if 'critical' in docstring.lower():
                tags.append('critical')
        
        return list(set(tags))  # 去重
    
    def _estimate_duration(self, complexity: str, is_async: bool) -> float:
        """估算测试持续时间（秒）"""
        base_duration = {
            'simple': 0.1,
            'medium': 0.5,
            'complex': 2.0,
            'unknown': 1.0
        }
        
        duration = base_duration.get(complexity, 1.0)
        
        # 异步测试通常需要更多时间
        if is_async:
            duration *= 1.5
        
        return duration
    
    def _extract_dependencies(self, test_file: Path) -> List[str]:
        """提取测试依赖"""
        try:
            content = test_file.read_text(encoding='utf-8')
            
            # 提取import语句
            dependencies = []
            
            # 查找import语句
            import_pattern = r'^(?:from\s+(\S+)\s+import|import\s+(\S+))'
            for line in content.split('\n'):
                match = re.match(import_pattern, line.strip())
                if match:
                    module = match.group(1) or match.group(2)
                    if module and not module.startswith('.'):
                        dependencies.append(module.split('.')[0])
            
            return list(set(dependencies))
            
        except:
            return []
    
    def _apply_filters(self,
                      tests: List[Dict[str, Any]],
                      module_filter: Optional[str],
                      test_type_filter: Optional[str]) -> List[Dict[str, Any]]:
        """应用过滤器"""
        filtered_tests = tests
        
        # 模块过滤器
        if module_filter:
            filtered_tests = [
                test for test in filtered_tests
                if test['module_name'] and module_filter.lower() in test['module_name'].lower()
            ]
        
        # 测试类型过滤器
        if test_type_filter:
            if test_type_filter in ['unit', 'integration']:
                # 按测试类型过滤
                filtered_tests = [
                    test for test in filtered_tests
                    if test['test_type'] == test_type_filter
                ]
            elif test_type_filter in ['comprehensive', 'simple', 'performance']:
                # 按测试子类型过滤
                filtered_tests = [
                    test for test in filtered_tests
                    if test['test_subtype'] == test_type_filter
                ]
            elif test_type_filter == 'smoke':
                # 冒烟测试：简单测试 + smoke标签
                filtered_tests = [
                    test for test in filtered_tests
                    if (test['test_subtype'] == 'simple' or 'smoke' in test['tags'])
                ]
        
        return filtered_tests
    
    def get_test_statistics(self) -> Dict[str, Any]:
        """获取测试统计信息"""
        # 发现所有测试
        all_tests = asyncio.run(self.discover_tests())
        
        # 统计信息
        stats = {
            'total_tests': len(all_tests),
            'by_module': {},
            'by_type': {},
            'by_subtype': {},
            'by_complexity': {},
            'async_tests': 0,
            'total_estimated_duration': 0
        }
        
        for test in all_tests:
            # 按模块统计
            module = test['module_name'] or 'unknown'
            stats['by_module'][module] = stats['by_module'].get(module, 0) + 1
            
            # 按类型统计
            test_type = test['test_type'] or 'unknown'
            stats['by_type'][test_type] = stats['by_type'].get(test_type, 0) + 1
            
            # 按子类型统计
            subtype = test['test_subtype']
            stats['by_subtype'][subtype] = stats['by_subtype'].get(subtype, 0) + 1
            
            # 按复杂度统计
            complexity = test['complexity']
            stats['by_complexity'][complexity] = stats['by_complexity'].get(complexity, 0) + 1
            
            # 异步测试统计
            if test['is_async']:
                stats['async_tests'] += 1
            
            # 总预估时间
            stats['total_estimated_duration'] += test['estimated_duration']
        
        return stats

