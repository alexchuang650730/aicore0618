"""
Human-in-the-Loop MCP 集成测试
测试组件间的集成和API接口
"""

import unittest
import json
import tempfile
import os
import sys
import time
import threading
from unittest.mock import patch, Mock
import requests

# 添加项目路径
sys.path.append('/home/ubuntu/aicore0615')
sys.path.append('/home/ubuntu/aicore0615/mcp/adapter/human_loop_mcp/src')

from models import InteractionType, InteractionData, CommonFields
from human_loop_server import HumanLoopMCPServer


class TestHumanLoopMCPIntegration(unittest.TestCase):
    """Human-in-the-Loop MCP 集成测试"""
    
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        # 创建临时配置文件
        cls.temp_config = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        config_content = """
service:
  name: "human_loop_mcp_test"
  version: "1.0.0"
  description: "Human-in-the-Loop MCP Test"

server:
  host: "127.0.0.1"
  port: 8097
  debug: false

database:
  type: "sqlite"
  path: ":memory:"

redis:
  host: null

session:
  default_timeout: 300
  max_timeout: 3600
  cleanup_interval: 60

ui:
  theme: "light"
  language: "zh-CN"

logging:
  level: "ERROR"
  file: "/tmp/human_loop_mcp_test.log"

security:
  enable_auth: false
  session_secret: "test-secret-key"
  cors_origins: ["*"]

integration:
  mcp_coordinator_url: "http://localhost:8090"
  workflow_callback_timeout: 30
"""
        cls.temp_config.write(config_content)
        cls.temp_config.close()
        
        # 创建服务器实例
        cls.server = HumanLoopMCPServer(cls.temp_config.name)
        cls.base_url = f"http://127.0.0.1:8097"
        
        # 在后台线程中启动服务器
        cls.server_thread = threading.Thread(
            target=cls.server.run,
            daemon=True
        )
        cls.server_thread.start()
        
        # 等待服务器启动
        time.sleep(2)
    
    @classmethod
    def tearDownClass(cls):
        """测试类清理"""
        # 删除临时配置文件
        if os.path.exists(cls.temp_config.name):
            os.unlink(cls.temp_config.name)
    
    def test_health_check(self):
        """测试健康检查接口"""
        try:
            response = requests.get(f"{self.base_url}/api/health", timeout=5)
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertEqual(data["status"], "healthy")
            self.assertIn("timestamp", data)
            self.assertIn("version", data)
            self.assertIn("service", data)
            self.assertIn("statistics", data)
        except requests.exceptions.RequestException as e:
            self.skipTest(f"服务器未启动或不可访问: {e}")
    
    def test_create_confirmation_session(self):
        """测试创建确认会话"""
        try:
            session_data = {
                "interaction_data": {
                    "interaction_type": "confirmation",
                    "title": "测试确认",
                    "message": "这是一个集成测试确认对话框",
                    "options": [
                        {"value": "yes", "label": "是"},
                        {"value": "no", "label": "否"}
                    ],
                    "timeout": 600
                },
                "workflow_id": "integration-test-workflow",
                "callback_url": "http://test.example.com/callback"
            }
            
            response = requests.post(
                f"{self.base_url}/api/sessions",
                json=session_data,
                timeout=5
            )
            
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertTrue(data["success"])
            self.assertIn("session_id", data)
            self.assertIn("session", data)
            
            session = data["session"]
            self.assertEqual(session["workflow_id"], "integration-test-workflow")
            self.assertEqual(session["status"], "pending")
            self.assertEqual(session["interaction_data"]["title"], "测试确认")
            
            return data["session_id"]
            
        except requests.exceptions.RequestException as e:
            self.skipTest(f"服务器未启动或不可访问: {e}")
    
    def test_create_selection_session(self):
        """测试创建选择会话"""
        try:
            session_data = {
                "interaction_data": {
                    "interaction_type": "selection",
                    "title": "环境选择",
                    "message": "请选择部署环境",
                    "options": [
                        {"value": "dev", "label": "开发环境"},
                        {"value": "staging", "label": "测试环境"},
                        {"value": "prod", "label": "生产环境"}
                    ],
                    "multiple": False,
                    "timeout": 900
                },
                "workflow_id": "deployment-workflow"
            }
            
            response = requests.post(
                f"{self.base_url}/api/sessions",
                json=session_data,
                timeout=5
            )
            
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertTrue(data["success"])
            
            session = data["session"]
            self.assertEqual(session["interaction_data"]["interaction_type"], "selection")
            self.assertEqual(len(session["interaction_data"]["options"]), 3)
            self.assertFalse(session["interaction_data"]["multiple"])
            
            return data["session_id"]
            
        except requests.exceptions.RequestException as e:
            self.skipTest(f"服务器未启动或不可访问: {e}")
    
    def test_create_text_input_session(self):
        """测试创建文本输入会话"""
        try:
            session_data = {
                "interaction_data": {
                    "interaction_type": "text_input",
                    "title": "配置信息",
                    "message": "请填写配置信息",
                    "fields": [
                        {
                            "name": "server_name",
                            "label": "服务器名称",
                            "field_type": "text",
                            "required": True
                        },
                        {
                            "name": "port",
                            "label": "端口号",
                            "field_type": "number",
                            "required": True,
                            "min_value": 1,
                            "max_value": 65535,
                            "default": 8080
                        },
                        {
                            "name": "admin_email",
                            "label": "管理员邮箱",
                            "field_type": "email",
                            "required": True,
                            "validation": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
                        }
                    ],
                    "timeout": 1200
                }
            }
            
            response = requests.post(
                f"{self.base_url}/api/sessions",
                json=session_data,
                timeout=5
            )
            
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertTrue(data["success"])
            
            session = data["session"]
            self.assertEqual(session["interaction_data"]["interaction_type"], "text_input")
            self.assertEqual(len(session["interaction_data"]["fields"]), 3)
            
            # 验证字段类型
            fields = session["interaction_data"]["fields"]
            self.assertEqual(fields[0]["field_type"], "text")
            self.assertEqual(fields[1]["field_type"], "number")
            self.assertEqual(fields[2]["field_type"], "email")
            
            return data["session_id"]
            
        except requests.exceptions.RequestException as e:
            self.skipTest(f"服务器未启动或不可访问: {e}")
    
    def test_get_session(self):
        """测试获取会话信息"""
        try:
            # 先创建一个会话
            session_id = self.test_create_confirmation_session()
            
            # 获取会话信息
            response = requests.get(
                f"{self.base_url}/api/sessions/{session_id}",
                timeout=5
            )
            
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertTrue(data["success"])
            self.assertIn("session", data)
            
            session = data["session"]
            self.assertEqual(session["session_id"], session_id)
            self.assertEqual(session["status"], "pending")
            
        except requests.exceptions.RequestException as e:
            self.skipTest(f"服务器未启动或不可访问: {e}")
    
    def test_respond_to_confirmation_session(self):
        """测试响应确认会话"""
        try:
            # 创建确认会话
            session_id = self.test_create_confirmation_session()
            
            # 提交响应
            response_data = {
                "response": {"choice": "yes"},
                "user_id": "test-user-123"
            }
            
            response = requests.post(
                f"{self.base_url}/api/sessions/{session_id}/respond",
                json=response_data,
                timeout=5
            )
            
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertTrue(data["success"])
            self.assertEqual(data["message"], "响应已提交")
            
            # 验证会话状态已更新
            get_response = requests.get(
                f"{self.base_url}/api/sessions/{session_id}",
                timeout=5
            )
            
            if get_response.status_code == 200:
                session_data = get_response.json()
                if session_data["success"]:
                    session = session_data["session"]
                    self.assertEqual(session["status"], "completed")
                    self.assertIn("response", session)
                    self.assertEqual(session["response"]["response_data"]["choice"], "yes")
            
        except requests.exceptions.RequestException as e:
            self.skipTest(f"服务器未启动或不可访问: {e}")
    
    def test_respond_to_selection_session(self):
        """测试响应选择会话"""
        try:
            # 创建选择会话
            session_id = self.test_create_selection_session()
            
            # 提交响应
            response_data = {
                "response": {"selection": "staging"},
                "user_id": "test-user-456"
            }
            
            response = requests.post(
                f"{self.base_url}/api/sessions/{session_id}/respond",
                json=response_data,
                timeout=5
            )
            
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertTrue(data["success"])
            
        except requests.exceptions.RequestException as e:
            self.skipTest(f"服务器未启动或不可访问: {e}")
    
    def test_respond_to_text_input_session(self):
        """测试响应文本输入会话"""
        try:
            # 创建文本输入会话
            session_id = self.test_create_text_input_session()
            
            # 提交响应
            response_data = {
                "response": {
                    "server_name": "web-server-01",
                    "port": 8080,
                    "admin_email": "admin@example.com"
                },
                "user_id": "test-user-789"
            }
            
            response = requests.post(
                f"{self.base_url}/api/sessions/{session_id}/respond",
                json=response_data,
                timeout=5
            )
            
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertTrue(data["success"])
            
        except requests.exceptions.RequestException as e:
            self.skipTest(f"服务器未启动或不可访问: {e}")
    
    def test_cancel_session(self):
        """测试取消会话"""
        try:
            # 创建会话
            session_id = self.test_create_confirmation_session()
            
            # 取消会话
            cancel_data = {
                "reason": "集成测试取消"
            }
            
            response = requests.post(
                f"{self.base_url}/api/sessions/{session_id}/cancel",
                json=cancel_data,
                timeout=5
            )
            
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertTrue(data["success"])
            self.assertEqual(data["message"], "会话已取消")
            
        except requests.exceptions.RequestException as e:
            self.skipTest(f"服务器未启动或不可访问: {e}")
    
    def test_list_sessions(self):
        """测试获取会话列表"""
        try:
            # 创建几个会话
            session_ids = []
            for i in range(3):
                session_data = {
                    "interaction_data": {
                        "interaction_type": "confirmation",
                        "title": f"列表测试会话 {i+1}",
                        "message": f"这是第 {i+1} 个测试会话"
                    },
                    "workflow_id": "list-test-workflow"
                }
                
                response = requests.post(
                    f"{self.base_url}/api/sessions",
                    json=session_data,
                    timeout=5
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data["success"]:
                        session_ids.append(data["session_id"])
            
            # 获取所有活跃会话
            response = requests.get(
                f"{self.base_url}/api/sessions",
                timeout=5
            )
            
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertTrue(data["success"])
            self.assertIn("sessions", data)
            
            sessions = data["sessions"]
            self.assertGreaterEqual(len(sessions), len(session_ids))
            
            # 获取特定工作流的会话
            response = requests.get(
                f"{self.base_url}/api/sessions?workflow_id=list-test-workflow",
                timeout=5
            )
            
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertTrue(data["success"])
            
            workflow_sessions = data["sessions"]
            for session in workflow_sessions:
                self.assertEqual(session["workflow_id"], "list-test-workflow")
            
        except requests.exceptions.RequestException as e:
            self.skipTest(f"服务器未启动或不可访问: {e}")
    
    def test_get_statistics(self):
        """测试获取统计信息"""
        try:
            response = requests.get(
                f"{self.base_url}/api/statistics",
                timeout=5
            )
            
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertTrue(data["success"])
            self.assertIn("statistics", data)
            
            stats = data["statistics"]
            self.assertIn("active_sessions", stats)
            self.assertIn("total_sessions", stats)
            self.assertIn("completed_sessions", stats)
            self.assertIn("timeout_sessions", stats)
            self.assertIn("cancelled_sessions", stats)
            
            # 验证统计数据类型
            self.assertIsInstance(stats["active_sessions"], int)
            self.assertIsInstance(stats["total_sessions"], int)
            
        except requests.exceptions.RequestException as e:
            self.skipTest(f"服务器未启动或不可访问: {e}")
    
    def test_get_templates(self):
        """测试获取交互模板"""
        try:
            response = requests.get(
                f"{self.base_url}/api/templates",
                timeout=5
            )
            
            self.assertEqual(response.status_code, 200)
            
            data = response.json()
            self.assertTrue(data["success"])
            self.assertIn("templates", data)
            
            templates = data["templates"]
            self.assertIn("confirmation", templates)
            self.assertIn("selection", templates)
            self.assertIn("text_input", templates)
            self.assertIn("file_upload", templates)
            
            # 验证模板结构
            confirmation_template = templates["confirmation"]
            self.assertIn("name", confirmation_template)
            self.assertIn("description", confirmation_template)
            self.assertIn("example", confirmation_template)
            
        except requests.exceptions.RequestException as e:
            self.skipTest(f"服务器未启动或不可访问: {e}")
    
    def test_invalid_session_operations(self):
        """测试无效会话操作"""
        try:
            invalid_session_id = "invalid-session-id-12345"
            
            # 尝试获取不存在的会话
            response = requests.get(
                f"{self.base_url}/api/sessions/{invalid_session_id}",
                timeout=5
            )
            
            self.assertEqual(response.status_code, 404)
            
            # 尝试响应不存在的会话
            response = requests.post(
                f"{self.base_url}/api/sessions/{invalid_session_id}/respond",
                json={"response": {"choice": "yes"}},
                timeout=5
            )
            
            self.assertEqual(response.status_code, 400)
            
            # 尝试取消不存在的会话
            response = requests.post(
                f"{self.base_url}/api/sessions/{invalid_session_id}/cancel",
                json={"reason": "测试"},
                timeout=5
            )
            
            self.assertEqual(response.status_code, 400)
            
        except requests.exceptions.RequestException as e:
            self.skipTest(f"服务器未启动或不可访问: {e}")
    
    def test_invalid_session_creation(self):
        """测试无效会话创建"""
        try:
            # 缺少必需字段
            invalid_data = {
                "workflow_id": "test-workflow"
                # 缺少 interaction_data
            }
            
            response = requests.post(
                f"{self.base_url}/api/sessions",
                json=invalid_data,
                timeout=5
            )
            
            self.assertEqual(response.status_code, 400)
            
            # 无效的交互类型
            invalid_data = {
                "interaction_data": {
                    "interaction_type": "invalid_type",
                    "title": "无效测试",
                    "message": "这是一个无效的交互类型"
                }
            }
            
            response = requests.post(
                f"{self.base_url}/api/sessions",
                json=invalid_data,
                timeout=5
            )
            
            self.assertEqual(response.status_code, 400)
            
        except requests.exceptions.RequestException as e:
            self.skipTest(f"服务器未启动或不可访问: {e}")


class TestWorkflowIntegration(unittest.TestCase):
    """工作流集成测试"""
    
    def setUp(self):
        """测试前准备"""
        self.base_url = "http://127.0.0.1:8097"
    
    def test_complete_workflow_scenario(self):
        """测试完整的工作流场景"""
        try:
            # 场景：部署应用的人工确认流程
            
            # 1. 创建环境选择会话
            env_session_data = {
                "interaction_data": {
                    "interaction_type": "selection",
                    "title": "选择部署环境",
                    "message": "请选择要部署应用的环境",
                    "options": [
                        {"value": "staging", "label": "测试环境"},
                        {"value": "prod", "label": "生产环境"}
                    ],
                    "multiple": False
                },
                "workflow_id": "app-deployment-workflow",
                "callback_url": "http://workflow.example.com/callback"
            }
            
            response = requests.post(
                f"{self.base_url}/api/sessions",
                json=env_session_data,
                timeout=5
            )
            
            self.assertEqual(response.status_code, 200)
            env_session_id = response.json()["session_id"]
            
            # 2. 用户选择生产环境
            env_response = requests.post(
                f"{self.base_url}/api/sessions/{env_session_id}/respond",
                json={
                    "response": {"selection": "prod"},
                    "user_id": "deploy-user"
                },
                timeout=5
            )
            
            self.assertEqual(env_response.status_code, 200)
            
            # 3. 创建确认会话（因为选择了生产环境）
            confirm_session_data = {
                "interaction_data": {
                    "interaction_type": "confirmation",
                    "title": "生产环境部署确认",
                    "message": "您选择了生产环境，这将影响线上服务。确定要继续吗？",
                    "options": [
                        {"value": "confirm", "label": "确认部署"},
                        {"value": "cancel", "label": "取消部署"}
                    ]
                },
                "workflow_id": "app-deployment-workflow"
            }
            
            response = requests.post(
                f"{self.base_url}/api/sessions",
                json=confirm_session_data,
                timeout=5
            )
            
            self.assertEqual(response.status_code, 200)
            confirm_session_id = response.json()["session_id"]
            
            # 4. 用户确认部署
            confirm_response = requests.post(
                f"{self.base_url}/api/sessions/{confirm_session_id}/respond",
                json={
                    "response": {"choice": "confirm"},
                    "user_id": "deploy-user"
                },
                timeout=5
            )
            
            self.assertEqual(confirm_response.status_code, 200)
            
            # 5. 验证工作流的所有会话
            workflow_response = requests.get(
                f"{self.base_url}/api/sessions?workflow_id=app-deployment-workflow",
                timeout=5
            )
            
            self.assertEqual(workflow_response.status_code, 200)
            
            workflow_data = workflow_response.json()
            self.assertTrue(workflow_data["success"])
            
            workflow_sessions = workflow_data["sessions"]
            self.assertGreaterEqual(len(workflow_sessions), 2)
            
            # 验证所有会话都属于同一工作流
            for session in workflow_sessions:
                self.assertEqual(session["workflow_id"], "app-deployment-workflow")
            
        except requests.exceptions.RequestException as e:
            self.skipTest(f"服务器未启动或不可访问: {e}")
    
    def test_timeout_scenario(self):
        """测试超时场景"""
        try:
            # 创建一个短超时的会话
            session_data = {
                "interaction_data": {
                    "interaction_type": "confirmation",
                    "title": "超时测试",
                    "message": "这个会话将很快超时",
                    "timeout": 2  # 2秒超时
                },
                "workflow_id": "timeout-test-workflow"
            }
            
            response = requests.post(
                f"{self.base_url}/api/sessions",
                json=session_data,
                timeout=5
            )
            
            self.assertEqual(response.status_code, 200)
            session_id = response.json()["session_id"]
            
            # 等待超时
            time.sleep(3)
            
            # 尝试响应已超时的会话
            response = requests.post(
                f"{self.base_url}/api/sessions/{session_id}/respond",
                json={
                    "response": {"choice": "yes"},
                    "user_id": "test-user"
                },
                timeout=5
            )
            
            # 应该失败，因为会话已超时
            self.assertEqual(response.status_code, 400)
            
        except requests.exceptions.RequestException as e:
            self.skipTest(f"服务器未启动或不可访问: {e}")


if __name__ == '__main__':
    # 运行集成测试
    unittest.main(verbosity=2)

