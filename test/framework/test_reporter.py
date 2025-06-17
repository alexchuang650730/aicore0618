#!/usr/bin/env python3
"""
PowerAutomation 测试报告生成器
负责生成各种格式的测试报告
"""

import asyncio
import logging
import json
import yaml
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import jinja2
import base64

class TestReporter:
    """
    PowerAutomation 测试报告生成器
    
    功能:
    - 生成JSON格式报告
    - 生成HTML格式报告
    - 生成趋势分析报告
    - 报告归档管理
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.project_root = Path("/opt/powerautomation")
        self.reports_dir = self.project_root / "test" / "reports"
        
        # 设置日志
        self.logger = logging.getLogger(__name__)
        
        # 报告配置
        self.output_formats = config.get('reporting', {}).get('formats', ['json'])
        self.include_logs = config.get('reporting', {}).get('include_logs', True)
        self.archive_days = config.get('reporting', {}).get('archive_days', 30)
        
        # 确保报告目录存在
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        (self.reports_dir / "daily").mkdir(exist_ok=True)
        (self.reports_dir / "weekly").mkdir(exist_ok=True)
        (self.reports_dir / "monthly").mkdir(exist_ok=True)
        
        # 初始化模板引擎
        self._setup_templates()
        
        self.logger.info("TestReporter initialized")
    
    def _setup_templates(self):
        """设置模板引擎"""
        # 创建模板目录
        template_dir = self.project_root / "test" / "templates"
        template_dir.mkdir(exist_ok=True)
        
        # 创建HTML报告模板
        self._create_html_template(template_dir)
        
        # 初始化Jinja2环境
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(template_dir)),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )
    
    def _create_html_template(self, template_dir: Path):
        """创建HTML报告模板"""
        html_template = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PowerAutomation 测试报告</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .header { text-align: center; margin-bottom: 30px; }
        .summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .summary-card { background: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }
        .summary-card h3 { margin: 0 0 10px 0; color: #333; }
        .summary-card .number { font-size: 2em; font-weight: bold; }
        .pass { color: #28a745; }
        .fail { color: #dc3545; }
        .error { color: #fd7e14; }
        .skip { color: #6c757d; }
        .test-table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        .test-table th, .test-table td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        .test-table th { background-color: #f8f9fa; font-weight: bold; }
        .status-badge { padding: 4px 8px; border-radius: 4px; color: white; font-size: 0.8em; }
        .status-pass { background-color: #28a745; }
        .status-fail { background-color: #dc3545; }
        .status-error { background-color: #fd7e14; }
        .status-skip { background-color: #6c757d; }
        .chart-container { margin: 20px 0; text-align: center; }
        .progress-bar { width: 100%; height: 20px; background-color: #e9ecef; border-radius: 10px; overflow: hidden; }
        .progress-fill { height: 100%; background: linear-gradient(90deg, #28a745 0%, #28a745 {{ summary.success_rate * 100 }}%, #dc3545 {{ summary.success_rate * 100 }}%); }
        .details { margin-top: 30px; }
        .collapsible { background-color: #f1f1f1; color: #444; cursor: pointer; padding: 18px; width: 100%; border: none; text-align: left; outline: none; font-size: 15px; }
        .collapsible:hover { background-color: #ddd; }
        .content { padding: 0 18px; display: none; overflow: hidden; background-color: #f9f9f9; }
        .timestamp { color: #666; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>PowerAutomation 测试报告</h1>
            <p class="timestamp">生成时间: {{ report_time }}</p>
            {% if session %}
            <p class="timestamp">测试会话: {{ session.session_id }}</p>
            {% endif %}
        </div>
        
        <div class="summary">
            <div class="summary-card">
                <h3>总测试数</h3>
                <div class="number">{{ summary.total }}</div>
            </div>
            <div class="summary-card">
                <h3>通过</h3>
                <div class="number pass">{{ summary.passed }}</div>
            </div>
            <div class="summary-card">
                <h3>失败</h3>
                <div class="number fail">{{ summary.failed }}</div>
            </div>
            <div class="summary-card">
                <h3>错误</h3>
                <div class="number error">{{ summary.errors }}</div>
            </div>
            <div class="summary-card">
                <h3>成功率</h3>
                <div class="number">{{ "%.1f"|format(summary.success_rate * 100) }}%</div>
            </div>
            <div class="summary-card">
                <h3>执行时间</h3>
                <div class="number">{{ "%.2f"|format(summary.duration) }}s</div>
            </div>
        </div>
        
        <div class="chart-container">
            <h3>测试结果概览</h3>
            <div class="progress-bar">
                <div class="progress-fill"></div>
            </div>
        </div>
        
        {% if session and session.results %}
        <div class="details">
            <h3>测试详情</h3>
            <table class="test-table">
                <thead>
                    <tr>
                        <th>测试名称</th>
                        <th>模块</th>
                        <th>类型</th>
                        <th>状态</th>
                        <th>耗时</th>
                        <th>错误信息</th>
                    </tr>
                </thead>
                <tbody>
                    {% for result in session.results %}
                    <tr>
                        <td>{{ result.test_name }}</td>
                        <td>{{ result.module_name or 'N/A' }}</td>
                        <td>{{ result.test_type or 'N/A' }}</td>
                        <td>
                            <span class="status-badge status-{{ result.status.lower() }}">
                                {{ result.status }}
                            </span>
                        </td>
                        <td>{{ "%.3f"|format(result.duration) }}s</td>
                        <td>{{ result.error_message or '' }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% endif %}
        
        {% if trends %}
        <div class="details">
            <h3>趋势分析</h3>
            <button class="collapsible">查看趋势数据</button>
            <div class="content">
                <pre>{{ trends | tojson(indent=2) }}</pre>
            </div>
        </div>
        {% endif %}
    </div>
    
    <script>
        // 折叠内容功能
        var coll = document.getElementsByClassName("collapsible");
        for (var i = 0; i < coll.length; i++) {
            coll[i].addEventListener("click", function() {
                this.classList.toggle("active");
                var content = this.nextElementSibling;
                if (content.style.display === "block") {
                    content.style.display = "none";
                } else {
                    content.style.display = "block";
                }
            });
        }
    </script>
</body>
</html>'''
        
        template_file = template_dir / "test_report.html"
        template_file.write_text(html_template, encoding='utf-8')
    
    async def generate_report(self,
                            report_data: Dict[str, Any],
                            report_type: str = 'session',
                            session_id: Optional[str] = None) -> Dict[str, str]:
        """
        生成测试报告
        
        Args:
            report_data: 报告数据
            report_type: 报告类型 (session, daily, weekly, monthly)
            session_id: 会话ID
        
        Returns:
            生成的报告文件路径字典
        """
        self.logger.info(f"Generating {report_type} report")
        
        # 准备报告数据
        processed_data = self._process_report_data(report_data, report_type)
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if session_id:
            base_name = f"{report_type}_report_{session_id}"
        else:
            base_name = f"{report_type}_report_{timestamp}"
        
        # 确定输出目录
        if report_type in ['daily', 'weekly', 'monthly']:
            output_dir = self.reports_dir / report_type
        else:
            output_dir = self.reports_dir
        
        output_dir.mkdir(exist_ok=True)
        
        # 生成各种格式的报告
        generated_files = {}
        
        for format_type in self.output_formats:
            try:
                if format_type == 'json':
                    file_path = await self._generate_json_report(processed_data, output_dir, base_name)
                    generated_files['json'] = str(file_path)
                elif format_type == 'html':
                    file_path = await self._generate_html_report(processed_data, output_dir, base_name)
                    generated_files['html'] = str(file_path)
                elif format_type == 'yaml':
                    file_path = await self._generate_yaml_report(processed_data, output_dir, base_name)
                    generated_files['yaml'] = str(file_path)
                
            except Exception as e:
                self.logger.error(f"Failed to generate {format_type} report: {e}")
        
        self.logger.info(f"Generated {len(generated_files)} report files")
        return generated_files
    
    def _process_report_data(self, report_data: Dict[str, Any], report_type: str) -> Dict[str, Any]:
        """处理报告数据"""
        processed = {
            'report_type': report_type,
            'report_time': datetime.now().isoformat(),
            'generator': 'PowerAutomation TestReporter v1.0',
            **report_data
        }
        
        # 添加趋势分析（如果是定期报告）
        if report_type in ['daily', 'weekly', 'monthly']:
            processed['trends'] = self._generate_trend_analysis(report_type)
        
        return processed
    
    def _generate_trend_analysis(self, report_type: str) -> Dict[str, Any]:
        """生成趋势分析"""
        # 简化的趋势分析
        # 实际实现应该从历史报告中提取数据
        return {
            'period': report_type,
            'analysis_time': datetime.now().isoformat(),
            'note': 'Trend analysis not fully implemented yet'
        }
    
    async def _generate_json_report(self, data: Dict[str, Any], output_dir: Path, base_name: str) -> Path:
        """生成JSON报告"""
        file_path = output_dir / f"{base_name}.json"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        
        self.logger.debug(f"Generated JSON report: {file_path}")
        return file_path
    
    async def _generate_html_report(self, data: Dict[str, Any], output_dir: Path, base_name: str) -> Path:
        """生成HTML报告"""
        file_path = output_dir / f"{base_name}.html"
        
        try:
            template = self.jinja_env.get_template('test_report.html')
            html_content = template.render(**data)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            self.logger.debug(f"Generated HTML report: {file_path}")
            return file_path
            
        except Exception as e:
            self.logger.error(f"Failed to generate HTML report: {e}")
            # 生成简化的HTML报告
            return await self._generate_simple_html_report(data, output_dir, base_name)
    
    async def _generate_simple_html_report(self, data: Dict[str, Any], output_dir: Path, base_name: str) -> Path:
        """生成简化的HTML报告"""
        file_path = output_dir / f"{base_name}_simple.html"
        
        summary = data.get('summary', {})
        
        html_content = f'''<!DOCTYPE html>
<html>
<head>
    <title>PowerAutomation 测试报告</title>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .summary {{ background: #f5f5f5; padding: 20px; border-radius: 5px; }}
        .pass {{ color: green; }}
        .fail {{ color: red; }}
        .error {{ color: orange; }}
    </style>
</head>
<body>
    <h1>PowerAutomation 测试报告</h1>
    <p>生成时间: {data.get('report_time', 'N/A')}</p>
    
    <div class="summary">
        <h2>测试摘要</h2>
        <p>总测试数: {summary.get('total', 0)}</p>
        <p class="pass">通过: {summary.get('passed', 0)}</p>
        <p class="fail">失败: {summary.get('failed', 0)}</p>
        <p class="error">错误: {summary.get('errors', 0)}</p>
        <p>成功率: {summary.get('success_rate', 0) * 100:.1f}%</p>
        <p>执行时间: {summary.get('duration', 0):.2f}秒</p>
    </div>
    
    <h2>详细数据</h2>
    <pre>{json.dumps(data, ensure_ascii=False, indent=2, default=str)}</pre>
</body>
</html>'''
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.logger.debug(f"Generated simple HTML report: {file_path}")
        return file_path
    
    async def _generate_yaml_report(self, data: Dict[str, Any], output_dir: Path, base_name: str) -> Path:
        """生成YAML报告"""
        file_path = output_dir / f"{base_name}.yaml"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
        
        self.logger.debug(f"Generated YAML report: {file_path}")
        return file_path
    
    async def generate_daily_report(self) -> Dict[str, str]:
        """生成日报告"""
        # 收集过去24小时的测试数据
        end_time = datetime.now()
        start_time = end_time - timedelta(days=1)
        
        # 简化实现 - 实际应该从测试历史中收集数据
        report_data = {
            'period': 'daily',
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'summary': {
                'total': 0,
                'passed': 0,
                'failed': 0,
                'errors': 0,
                'success_rate': 0,
                'duration': 0
            },
            'note': 'Daily report generation not fully implemented'
        }
        
        return await self.generate_report(report_data, 'daily')
    
    async def generate_weekly_report(self) -> Dict[str, str]:
        """生成周报告"""
        # 收集过去7天的测试数据
        end_time = datetime.now()
        start_time = end_time - timedelta(days=7)
        
        report_data = {
            'period': 'weekly',
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'summary': {
                'total': 0,
                'passed': 0,
                'failed': 0,
                'errors': 0,
                'success_rate': 0,
                'duration': 0
            },
            'note': 'Weekly report generation not fully implemented'
        }
        
        return await self.generate_report(report_data, 'weekly')
    
    async def generate_monthly_report(self) -> Dict[str, str]:
        """生成月报告"""
        # 收集过去30天的测试数据
        end_time = datetime.now()
        start_time = end_time - timedelta(days=30)
        
        report_data = {
            'period': 'monthly',
            'start_time': start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'summary': {
                'total': 0,
                'passed': 0,
                'failed': 0,
                'errors': 0,
                'success_rate': 0,
                'duration': 0
            },
            'note': 'Monthly report generation not fully implemented'
        }
        
        return await self.generate_report(report_data, 'monthly')
    
    def list_reports(self, report_type: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """列出报告文件"""
        reports = []
        
        # 确定搜索目录
        if report_type and report_type in ['daily', 'weekly', 'monthly']:
            search_dirs = [self.reports_dir / report_type]
        else:
            search_dirs = [
                self.reports_dir,
                self.reports_dir / 'daily',
                self.reports_dir / 'weekly',
                self.reports_dir / 'monthly'
            ]
        
        # 搜索报告文件
        for search_dir in search_dirs:
            if search_dir.exists():
                for file_path in search_dir.glob('*.json'):
                    try:
                        stat = file_path.stat()
                        reports.append({
                            'file_path': str(file_path),
                            'file_name': file_path.name,
                            'file_size': stat.st_size,
                            'created_time': datetime.fromtimestamp(stat.st_ctime),
                            'modified_time': datetime.fromtimestamp(stat.st_mtime),
                            'report_type': file_path.parent.name if file_path.parent.name in ['daily', 'weekly', 'monthly'] else 'session'
                        })
                    except Exception as e:
                        self.logger.warning(f"Failed to get info for {file_path}: {e}")
        
        # 按修改时间排序
        reports.sort(key=lambda x: x['modified_time'], reverse=True)
        
        # 限制数量
        if limit > 0:
            reports = reports[:limit]
        
        return reports
    
    async def cleanup_old_reports(self) -> int:
        """清理旧报告"""
        if self.archive_days <= 0:
            return 0
        
        cutoff_date = datetime.now() - timedelta(days=self.archive_days)
        cleaned_count = 0
        
        # 搜索所有报告文件
        for report_file in self.reports_dir.rglob('*.json'):
            try:
                if datetime.fromtimestamp(report_file.stat().st_mtime) < cutoff_date:
                    report_file.unlink()
                    cleaned_count += 1
                    self.logger.debug(f"Cleaned old report: {report_file}")
            except Exception as e:
                self.logger.warning(f"Failed to clean report {report_file}: {e}")
        
        # 清理对应的HTML和YAML文件
        for report_file in self.reports_dir.rglob('*.html'):
            try:
                if datetime.fromtimestamp(report_file.stat().st_mtime) < cutoff_date:
                    report_file.unlink()
                    cleaned_count += 1
            except Exception as e:
                self.logger.warning(f"Failed to clean HTML report {report_file}: {e}")
        
        for report_file in self.reports_dir.rglob('*.yaml'):
            try:
                if datetime.fromtimestamp(report_file.stat().st_mtime) < cutoff_date:
                    report_file.unlink()
                    cleaned_count += 1
            except Exception as e:
                self.logger.warning(f"Failed to clean YAML report {report_file}: {e}")
        
        self.logger.info(f"Cleaned {cleaned_count} old report files")
        return cleaned_count
    
    async def cleanup(self):
        """清理资源"""
        # 清理旧报告
        await self.cleanup_old_reports()
        self.logger.info("TestReporter cleanup completed")

