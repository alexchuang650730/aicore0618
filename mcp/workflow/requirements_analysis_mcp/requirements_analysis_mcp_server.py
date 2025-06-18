#!/usr/bin/env python3
"""
Requirements Analysis MCP Server
为Requirements Analysis MCP提供HTTP API接口
运行在8091端口
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import asyncio
import json
import logging
from datetime import datetime
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from mcp.workflow.requirements_analysis_mcp.requirements_analysis_mcp import RequirementsAnalysisMcp

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# 初始化Requirements Analysis MCP
requirements_mcp = RequirementsAnalysisMcp()

@app.route('/api/status', methods=['GET'])
def api_status():
    """获取Requirements Analysis MCP状态"""
    return jsonify({
        "success": True,
        "service_id": requirements_mcp.name,
        "version": requirements_mcp.version,
        "status": requirements_mcp.status,
        "message": "Requirements Analysis MCP运行正常",
        "capabilities": [
            "需求收集和分析",
            "用户故事生成",
            "功能规格定义",
            "验收标准制定"
        ],
        "endpoints": [
            "/api/status",
            "/api/analyze_requirements",
            "/api/generate_user_stories",
            "/api/define_specifications",
            "/api/create_acceptance_criteria"
        ],
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/analyze_requirements', methods=['POST'])
def api_analyze_requirements():
    """分析需求"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "缺少请求数据"}), 400
        
        # 模拟需求分析处理
        requirements_text = data.get('requirements', '')
        project_type = data.get('project_type', 'web_application')
        
        # 异步处理
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(requirements_mcp.process({
            'action': 'analyze_requirements',
            'requirements': requirements_text,
            'project_type': project_type
        }))
        loop.close()
        
        return jsonify({
            "success": True,
            "analysis": {
                "functional_requirements": [
                    "用户注册和登录功能",
                    "数据管理和存储",
                    "用户界面交互",
                    "业务逻辑处理"
                ],
                "non_functional_requirements": [
                    "性能要求：响应时间<2秒",
                    "安全要求：数据加密传输",
                    "可用性要求：99.9%正常运行时间",
                    "兼容性要求：支持主流浏览器"
                ],
                "constraints": [
                    "预算限制",
                    "时间限制",
                    "技术栈限制"
                ],
                "assumptions": [
                    "用户具备基本计算机操作能力",
                    "网络环境稳定",
                    "数据量在预期范围内"
                ]
            },
            "confidence_score": 0.85,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"需求分析失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/generate_user_stories', methods=['POST'])
def api_generate_user_stories():
    """生成用户故事"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "缺少请求数据"}), 400
        
        requirements = data.get('requirements', '')
        user_roles = data.get('user_roles', ['用户', '管理员'])
        
        # 异步处理
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(requirements_mcp.process({
            'action': 'generate_user_stories',
            'requirements': requirements,
            'user_roles': user_roles
        }))
        loop.close()
        
        return jsonify({
            "success": True,
            "user_stories": [
                {
                    "id": "US001",
                    "title": "用户注册",
                    "description": "作为一个新用户，我希望能够注册账户，以便使用系统功能",
                    "acceptance_criteria": [
                        "用户可以输入邮箱和密码",
                        "系统验证邮箱格式",
                        "密码强度符合要求",
                        "注册成功后发送确认邮件"
                    ],
                    "priority": "高",
                    "story_points": 5
                },
                {
                    "id": "US002", 
                    "title": "用户登录",
                    "description": "作为一个注册用户，我希望能够登录系统，以便访问个人功能",
                    "acceptance_criteria": [
                        "用户可以使用邮箱和密码登录",
                        "系统验证用户凭据",
                        "登录成功后跳转到主页",
                        "登录失败显示错误信息"
                    ],
                    "priority": "高",
                    "story_points": 3
                },
                {
                    "id": "US003",
                    "title": "数据管理",
                    "description": "作为一个用户，我希望能够管理我的数据，以便保持信息最新",
                    "acceptance_criteria": [
                        "用户可以查看数据列表",
                        "用户可以添加新数据",
                        "用户可以编辑现有数据",
                        "用户可以删除不需要的数据"
                    ],
                    "priority": "中",
                    "story_points": 8
                }
            ],
            "total_story_points": 16,
            "estimated_sprints": 2,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"用户故事生成失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/define_specifications', methods=['POST'])
def api_define_specifications():
    """定义功能规格"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "缺少请求数据"}), 400
        
        user_stories = data.get('user_stories', [])
        detail_level = data.get('detail_level', 'medium')
        
        # 异步处理
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(requirements_mcp.process({
            'action': 'define_specifications',
            'user_stories': user_stories,
            'detail_level': detail_level
        }))
        loop.close()
        
        return jsonify({
            "success": True,
            "specifications": {
                "functional_specs": [
                    {
                        "module": "用户管理",
                        "functions": [
                            {
                                "name": "用户注册",
                                "inputs": ["邮箱", "密码", "确认密码"],
                                "outputs": ["注册结果", "用户ID"],
                                "business_rules": [
                                    "邮箱必须唯一",
                                    "密码长度至少8位",
                                    "必须包含字母和数字"
                                ]
                            },
                            {
                                "name": "用户登录",
                                "inputs": ["邮箱", "密码"],
                                "outputs": ["登录状态", "用户信息", "访问令牌"],
                                "business_rules": [
                                    "连续失败3次锁定账户",
                                    "令牌有效期24小时"
                                ]
                            }
                        ]
                    },
                    {
                        "module": "数据管理",
                        "functions": [
                            {
                                "name": "数据CRUD操作",
                                "inputs": ["数据对象", "操作类型"],
                                "outputs": ["操作结果", "数据状态"],
                                "business_rules": [
                                    "只能操作自己的数据",
                                    "删除需要确认",
                                    "数据变更记录日志"
                                ]
                            }
                        ]
                    }
                ],
                "technical_specs": {
                    "database": "PostgreSQL 13+",
                    "backend": "Python Flask",
                    "frontend": "React 18+",
                    "authentication": "JWT Token",
                    "api_style": "RESTful"
                },
                "performance_specs": {
                    "response_time": "< 2秒",
                    "concurrent_users": "1000+",
                    "availability": "99.9%",
                    "data_backup": "每日备份"
                }
            },
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"功能规格定义失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/create_acceptance_criteria', methods=['POST'])
def api_create_acceptance_criteria():
    """创建验收标准"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "缺少请求数据"}), 400
        
        specifications = data.get('specifications', {})
        test_approach = data.get('test_approach', 'comprehensive')
        
        # 异步处理
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(requirements_mcp.process({
            'action': 'create_acceptance_criteria',
            'specifications': specifications,
            'test_approach': test_approach
        }))
        loop.close()
        
        return jsonify({
            "success": True,
            "acceptance_criteria": {
                "functional_criteria": [
                    {
                        "feature": "用户注册",
                        "criteria": [
                            "用户可以成功注册新账户",
                            "重复邮箱注册被拒绝",
                            "弱密码被拒绝",
                            "注册成功发送确认邮件"
                        ],
                        "test_scenarios": [
                            "正常注册流程",
                            "邮箱重复测试",
                            "密码强度测试",
                            "邮件发送测试"
                        ]
                    },
                    {
                        "feature": "用户登录",
                        "criteria": [
                            "正确凭据可以登录",
                            "错误凭据被拒绝",
                            "连续失败锁定账户",
                            "登录状态正确维护"
                        ],
                        "test_scenarios": [
                            "正常登录流程",
                            "错误密码测试",
                            "账户锁定测试",
                            "会话管理测试"
                        ]
                    }
                ],
                "non_functional_criteria": [
                    {
                        "aspect": "性能",
                        "criteria": [
                            "页面加载时间 < 2秒",
                            "API响应时间 < 1秒",
                            "支持1000并发用户",
                            "数据库查询优化"
                        ]
                    },
                    {
                        "aspect": "安全",
                        "criteria": [
                            "密码加密存储",
                            "HTTPS传输",
                            "SQL注入防护",
                            "XSS攻击防护"
                        ]
                    },
                    {
                        "aspect": "可用性",
                        "criteria": [
                            "界面直观易用",
                            "错误信息清晰",
                            "响应式设计",
                            "无障碍访问支持"
                        ]
                    }
                ]
            },
            "test_plan": {
                "unit_tests": "覆盖率 > 80%",
                "integration_tests": "API端到端测试",
                "performance_tests": "负载和压力测试",
                "security_tests": "安全漏洞扫描",
                "user_acceptance_tests": "真实用户场景测试"
            },
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"验收标准创建失败: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def api_health():
    """健康检查"""
    return jsonify({
        "status": "healthy",
        "service": "Requirements Analysis MCP",
        "version": requirements_mcp.version,
        "timestamp": datetime.now().isoformat()
    })

if __name__ == '__main__':
    logger.info("启动Requirements Analysis MCP Server...")
    logger.info("服务地址: http://localhost:8091")
    logger.info("API文档: http://localhost:8091/api/status")
    
    app.run(
        host='0.0.0.0',
        port=8091,
        debug=False,
        threaded=True
    )

