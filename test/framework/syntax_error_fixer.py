#!/usr/bin/env python3
"""
PowerAutomation 语法错误修复器
修复测试文件中的语法错误
"""

import os
import sys
import re
from pathlib import Path
import logging

class SyntaxErrorFixer:
    """语法错误修复器"""
    
    def __init__(self):
        self.project_root = Path("/opt/powerautomation")
        self.fixed_count = 0
        self.error_count = 0
        
        # 设置日志
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def fix_all_syntax_errors(self):
        """修复所有语法错误"""
        self.logger.info("开始修复语法错误...")
        
        # 查找所有comprehensive测试文件
        test_files = []
        for pattern in ["**/test_*_comprehensive.py"]:
            test_files.extend(self.project_root.glob(pattern))
        
        for test_file in test_files:
            try:
                self._fix_file_syntax(test_file)
            except Exception as e:
                self.logger.error(f"修复文件失败 {test_file}: {e}")
                self.error_count += 1
        
        self.logger.info(f"修复完成: {self.fixed_count} 个文件已修复, {self.error_count} 个错误")
    
    def _fix_file_syntax(self, test_file: Path):
        """修复单个文件的语法错误"""
        content = test_file.read_text(encoding='utf-8')
        original_content = content
        
        # 修复try语句后缺少缩进的问题
        content = self._fix_try_statements(content)
        
        # 修复导入语句的语法错误
        content = self._fix_import_statements(content)
        
        # 修复其他常见语法错误
        content = self._fix_common_syntax_errors(content)
        
        # 如果内容有变化，写回文件
        if content != original_content:
            test_file.write_text(content, encoding='utf-8')
            self.fixed_count += 1
            self.logger.info(f"修复语法错误: {test_file}")
    
    def _fix_try_statements(self, content: str) -> str:
        """修复try语句后缺少缩进的问题"""
        # 查找try语句后面没有正确缩进的情况
        lines = content.split('\n')
        fixed_lines = []
        
        i = 0
        while i < len(lines):
            line = lines[i]
            fixed_lines.append(line)
            
            # 检查是否是try语句
            if re.match(r'\s*try:\s*$', line):
                # 检查下一行是否正确缩进
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    # 如果下一行是except或者没有正确缩进，添加pass语句
                    if (re.match(r'\s*except\s+', next_line) or 
                        not next_line.strip() or 
                        not next_line.startswith('    ')):
                        # 获取当前行的缩进
                        indent = len(line) - len(line.lstrip())
                        fixed_lines.append(' ' * (indent + 4) + 'pass')
            
            i += 1
        
        return '\n'.join(fixed_lines)
    
    def _fix_import_statements(self, content: str) -> str:
        """修复导入语句的语法错误"""
        # 修复行继续字符后的问题
        content = re.sub(r'\\\s*\n\s*from', r'\nfrom', content)
        content = re.sub(r'\\\s*\n\s*import', r'\nimport', content)
        
        # 修复多行导入语句
        content = re.sub(r'try:\s*\n\s*from mcp\.\s*\n', 'try:\n    from mcp.', content)
        content = re.sub(r'try:\s*\n\s*import mcp\.\s*\n', 'try:\n    import mcp.', content)
        
        return content
    
    def _fix_common_syntax_errors(self, content: str) -> str:
        """修复其他常见语法错误"""
        # 修复空的except块
        content = re.sub(r'except ImportError:\s*\n(\s*)#', r'except ImportError:\n\1    pass\n\1#', content)
        
        # 修复空的if块
        content = re.sub(r'if\s+.*?:\s*\n(\s*)#', r'if True:\n\1    pass\n\1#', content)
        
        # 修复空的class定义
        content = re.sub(r'class\s+\w+.*?:\s*\n(\s*)#', r'class MockClass:\n\1    pass\n\1#', content)
        
        return content

def main():
    """主函数"""
    fixer = SyntaxErrorFixer()
    fixer.fix_all_syntax_errors()
    print(f"修复完成: {fixer.fixed_count} 个文件已修复, {fixer.error_count} 个错误")

if __name__ == "__main__":
    main()

