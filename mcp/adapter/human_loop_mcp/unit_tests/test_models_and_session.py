"""
Human-in-the-Loop MCP 单元测试
测试核心组件的功能
"""

import unittest
import json
import tempfile
import os
import sys
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# 添加项目路径
sys.path.append('/home/ubuntu/aicore0615')
sys.path.append('/home/ubuntu/aicore0615/mcp/adapter/human_loop_mcp/src')

from models import (
    InteractionType, SessionStatus, InteractionField, InteractionData, 
    UserResponse, InteractionSession, InteractionTemplates, CommonFields
)
from session_manager import SessionManager


class TestModels(unittest.TestCase):
    """测试数据模型"""
    
    def test_interaction_field_creation(self):
        """测试交互字段创建"""
        field = InteractionField(
            name="test_field",
            label="测试字段",
            field_type="text",
            required=True,
            default="默认值"
        )
        
        self.assertEqual(field.name, "test_field")
        self.assertEqual(field.label, "测试字段")
        self.assertEqual(field.field_type, "text")
        self.assertTrue(field.required)
        self.assertEqual(field.default, "默认值")
    
    def test_interaction_field_to_dict(self):
        """测试交互字段转换为字典"""
        field = InteractionField(
            name="email",
            label="邮箱地址",
            field_type="email",
            required=True,
            validation=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        )
        
        field_dict = field.to_dict()
        self.assertIsInstance(field_dict, dict)
        self.assertEqual(field_dict['name'], "email")
        self.assertEqual(field_dict['field_type'], "email")
        self.assertTrue(field_dict['required'])
    
    def test_interaction_data_creation(self):
        """测试交互数据创建"""
        fields = [
            InteractionField("name", "姓名", "text", True),
            InteractionField("age", "年龄", "number", False, 18)
        ]
        
        interaction_data = InteractionData(
            interaction_type=InteractionType.TEXT_INPUT,
            title="用户信息",
            message="请填写用户信息",
            fields=fields,
            timeout=600
        )
        
        self.assertEqual(interaction_data.interaction_type, InteractionType.TEXT_INPUT)
        self.assertEqual(interaction_data.title, "用户信息")
        self.assertEqual(len(interaction_data.fields), 2)
        self.assertEqual(interaction_data.timeout, 600)
    
    def test_interaction_data_to_dict(self):
        """测试交互数据转换为字典"""
        interaction_data = InteractionData(
            interaction_type=InteractionType.CONFIRMATION,
            title="确认操作",
            message="是否继续？",
            options=[{"value": "yes", "label": "是"}, {"value": "no", "label": "否"}]
        )
        
        data_dict = interaction_data.to_dict()
        self.assertIsInstance(data_dict, dict)
        self.assertEqual(data_dict['interaction_type'], 'confirmation')
        self.assertEqual(data_dict['title'], "确认操作")
        self.assertIsInstance(data_dict['options'], list)
    
    def test_user_response_creation(self):
        """测试用户响应创建"""
        response = UserResponse(
            session_id="test-session-123",
            response_data={"choice": "yes"},
            submitted_at=datetime.now(),
            user_id="user-456"
        )
        
        self.assertEqual(response.session_id, "test-session-123")
        self.assertEqual(response.response_data["choice"], "yes")
        self.assertEqual(response.user_id, "user-456")
    
    def test_interaction_session_creation(self):
        """测试交互会话创建"""
        interaction_data = InteractionData(
            interaction_type=InteractionType.CONFIRMATION,
            title="测试确认",
            message="这是一个测试",
            timeout=300
        )
        
        session = InteractionSession(
            interaction_data=interaction_data,
            workflow_id="workflow-123",
            callback_url="http://example.com/callback"
        )
        
        self.assertIsNotNone(session.session_id)
        self.assertEqual(session.workflow_id, "workflow-123")
        self.assertEqual(session.callback_url, "http://example.com/callback")
        self.assertEqual(session.status, SessionStatus.PENDING)
        self.assertIsNotNone(session.created_at)
        self.assertIsNotNone(session.expires_at)
    
    def test_interaction_session_expiry(self):
        """测试会话过期检查"""
        # 创建已过期的会话
        interaction_data = InteractionData(
            interaction_type=InteractionType.CONFIRMATION,
            title="过期测试",
            message="这个会话应该已过期",
            timeout=1  # 1秒超时
        )
        
        session = InteractionSession(interaction_data=interaction_data)
        
        # 手动设置过期时间为过去
        session.expires_at = datetime.now() - timedelta(seconds=10)
        
        self.assertTrue(session.is_expired())
    
    def test_interaction_session_response(self):
        """测试会话响应设置"""
        interaction_data = InteractionData(
            interaction_type=InteractionType.CONFIRMATION,
            title="响应测试",
            message="测试响应功能"
        )
        
        session = InteractionSession(interaction_data=interaction_data)
        
        # 设置响应
        response_data = {"choice": "confirm"}
        session.set_response(response_data, "user-123")
        
        self.assertEqual(session.status, SessionStatus.COMPLETED)
        self.assertIsNotNone(session.response)
        self.assertEqual(session.response.response_data["choice"], "confirm")
        self.assertEqual(session.response.user_id, "user-123")
    
    def test_interaction_session_to_dict(self):
        """测试会话转换为字典"""
        interaction_data = InteractionData(
            interaction_type=InteractionType.SELECTION,
            title="选择测试",
            message="请选择一个选项",
            options=[{"value": "a", "label": "选项A"}]
        )
        
        session = InteractionSession(interaction_data=interaction_data)
        session_dict = session.to_dict()
        
        self.assertIsInstance(session_dict, dict)
        self.assertIn('session_id', session_dict)
        self.assertIn('status', session_dict)
        self.assertIn('interaction_data', session_dict)
        self.assertEqual(session_dict['status'], 'pending')
    
    def test_interaction_session_from_dict(self):
        """测试从字典创建会话"""
        session_data = {
            'session_id': 'test-session-456',
            'workflow_id': 'workflow-789',
            'status': 'pending',
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(minutes=5)).isoformat(),
            'interaction_data': {
                'interaction_type': 'confirmation',
                'title': '测试标题',
                'message': '测试消息',
                'timeout': 300
            }
        }
        
        session = InteractionSession.from_dict(session_data)
        
        self.assertEqual(session.session_id, 'test-session-456')
        self.assertEqual(session.workflow_id, 'workflow-789')
        self.assertEqual(session.status, SessionStatus.PENDING)
        self.assertEqual(session.interaction_data.title, '测试标题')


class TestInteractionTemplates(unittest.TestCase):
    """测试交互模板"""
    
    def test_confirmation_template(self):
        """测试确认对话框模板"""
        template = InteractionTemplates.confirmation(
            "确认删除",
            "确定要删除这个文件吗？",
            timeout=600
        )
        
        self.assertEqual(template.interaction_type, InteractionType.CONFIRMATION)
        self.assertEqual(template.title, "确认删除")
        self.assertEqual(template.message, "确定要删除这个文件吗？")
        self.assertEqual(template.timeout, 600)
        self.assertIsNotNone(template.options)
        self.assertEqual(len(template.options), 2)
    
    def test_selection_template(self):
        """测试选择对话框模板"""
        options = [
            {"value": "dev", "label": "开发环境"},
            {"value": "staging", "label": "测试环境"},
            {"value": "prod", "label": "生产环境"}
        ]
        
        template = InteractionTemplates.selection(
            "选择环境",
            "请选择部署环境",
            options,
            multiple=False,
            timeout=900
        )
        
        self.assertEqual(template.interaction_type, InteractionType.SELECTION)
        self.assertEqual(template.title, "选择环境")
        self.assertEqual(len(template.options), 3)
        self.assertFalse(template.multiple)
        self.assertEqual(template.timeout, 900)
    
    def test_text_input_template(self):
        """测试文本输入模板"""
        fields = [
            CommonFields.text_field("name", "姓名", True),
            CommonFields.email_field("email", "邮箱", True),
            CommonFields.number_field("age", "年龄", False, 18, 1, 120)
        ]
        
        template = InteractionTemplates.text_input(
            "用户信息",
            "请填写用户信息",
            fields,
            timeout=1200
        )
        
        self.assertEqual(template.interaction_type, InteractionType.TEXT_INPUT)
        self.assertEqual(template.title, "用户信息")
        self.assertEqual(len(template.fields), 3)
        self.assertEqual(template.timeout, 1200)
    
    def test_file_upload_template(self):
        """测试文件上传模板"""
        template = InteractionTemplates.file_upload(
            "上传配置",
            "请上传配置文件",
            accept_types=[".json", ".yaml"],
            max_file_size="5MB",
            multiple=True
        )
        
        self.assertEqual(template.interaction_type, InteractionType.FILE_UPLOAD)
        self.assertEqual(template.title, "上传配置")
        self.assertEqual(template.accept_types, [".json", ".yaml"])
        self.assertEqual(template.max_file_size, "5MB")
        self.assertTrue(template.multiple)


class TestCommonFields(unittest.TestCase):
    """测试常用字段"""
    
    def test_text_field(self):
        """测试文本字段"""
        field = CommonFields.text_field(
            "username",
            "用户名",
            required=True,
            default="admin",
            validation=r"^[a-zA-Z0-9_]+$"
        )
        
        self.assertEqual(field.name, "username")
        self.assertEqual(field.label, "用户名")
        self.assertEqual(field.field_type, "text")
        self.assertTrue(field.required)
        self.assertEqual(field.default, "admin")
        self.assertEqual(field.validation, r"^[a-zA-Z0-9_]+$")
    
    def test_number_field(self):
        """测试数字字段"""
        field = CommonFields.number_field(
            "port",
            "端口号",
            required=True,
            default=8080,
            min_value=1,
            max_value=65535
        )
        
        self.assertEqual(field.name, "port")
        self.assertEqual(field.field_type, "number")
        self.assertEqual(field.default, 8080)
        self.assertEqual(field.min_value, 1)
        self.assertEqual(field.max_value, 65535)
    
    def test_email_field(self):
        """测试邮箱字段"""
        field = CommonFields.email_field("email", "邮箱地址", True)
        
        self.assertEqual(field.name, "email")
        self.assertEqual(field.field_type, "email")
        self.assertTrue(field.required)
        self.assertIsNotNone(field.validation)
    
    def test_url_field(self):
        """测试URL字段"""
        field = CommonFields.url_field("website", "网站地址", False)
        
        self.assertEqual(field.name, "website")
        self.assertEqual(field.field_type, "url")
        self.assertFalse(field.required)
        self.assertIsNotNone(field.validation)
    
    def test_select_field(self):
        """测试选择字段"""
        options = [
            {"value": "small", "label": "小"},
            {"value": "medium", "label": "中"},
            {"value": "large", "label": "大"}
        ]
        
        field = CommonFields.select_field(
            "size",
            "尺寸",
            options,
            required=True,
            default="medium"
        )
        
        self.assertEqual(field.name, "size")
        self.assertEqual(field.field_type, "select")
        self.assertEqual(len(field.options), 3)
        self.assertEqual(field.default, "medium")


class TestSessionManager(unittest.TestCase):
    """测试会话管理器"""
    
    def setUp(self):
        """测试前准备"""
        # 创建临时数据库
        self.temp_db = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        self.temp_db.close()
        
        # 测试配置
        self.config = {
            'database': {
                'type': 'sqlite',
                'path': self.temp_db.name
            },
            'redis': {
                'host': None  # 禁用Redis用于测试
            },
            'session': {
                'default_timeout': 300,
                'max_timeout': 3600,
                'cleanup_interval': 60
            }
        }
        
        # 创建会话管理器
        with patch('threading.Thread'):  # 禁用清理线程
            self.session_manager = SessionManager(self.config)
    
    def tearDown(self):
        """测试后清理"""
        # 删除临时数据库
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_create_session(self):
        """测试创建会话"""
        interaction_data = InteractionData(
            interaction_type=InteractionType.CONFIRMATION,
            title="测试会话",
            message="这是一个测试会话"
        )
        
        session = self.session_manager.create_session(
            interaction_data=interaction_data,
            workflow_id="test-workflow",
            callback_url="http://test.com/callback"
        )
        
        self.assertIsNotNone(session.session_id)
        self.assertEqual(session.workflow_id, "test-workflow")
        self.assertEqual(session.callback_url, "http://test.com/callback")
        self.assertEqual(session.status, SessionStatus.PENDING)
        
        # 验证会话已保存到内存
        self.assertIn(session.session_id, self.session_manager.active_sessions)
    
    def test_get_session(self):
        """测试获取会话"""
        # 创建会话
        interaction_data = InteractionData(
            interaction_type=InteractionType.SELECTION,
            title="获取测试",
            message="测试获取会话功能"
        )
        
        created_session = self.session_manager.create_session(interaction_data)
        
        # 获取会话
        retrieved_session = self.session_manager.get_session(created_session.session_id)
        
        self.assertIsNotNone(retrieved_session)
        self.assertEqual(retrieved_session.session_id, created_session.session_id)
        self.assertEqual(retrieved_session.interaction_data.title, "获取测试")
    
    def test_complete_session(self):
        """测试完成会话"""
        # 创建会话
        interaction_data = InteractionData(
            interaction_type=InteractionType.CONFIRMATION,
            title="完成测试",
            message="测试完成会话功能"
        )
        
        session = self.session_manager.create_session(interaction_data)
        
        # 完成会话
        response_data = {"choice": "confirm"}
        success = self.session_manager.complete_session(
            session.session_id,
            response_data,
            "test-user"
        )
        
        self.assertTrue(success)
        
        # 验证会话状态
        updated_session = self.session_manager.get_session(session.session_id)
        self.assertEqual(updated_session.status, SessionStatus.COMPLETED)
        self.assertIsNotNone(updated_session.response)
        self.assertEqual(updated_session.response.response_data["choice"], "confirm")
        
        # 验证会话已从活跃列表中移除
        self.assertNotIn(session.session_id, self.session_manager.active_sessions)
    
    def test_cancel_session(self):
        """测试取消会话"""
        # 创建会话
        interaction_data = InteractionData(
            interaction_type=InteractionType.TEXT_INPUT,
            title="取消测试",
            message="测试取消会话功能"
        )
        
        session = self.session_manager.create_session(interaction_data)
        
        # 取消会话
        success = self.session_manager.cancel_session(
            session.session_id,
            "用户取消"
        )
        
        self.assertTrue(success)
        
        # 验证会话状态
        updated_session = self.session_manager.get_session(session.session_id)
        self.assertEqual(updated_session.status, SessionStatus.CANCELLED)
        self.assertEqual(updated_session.error_message, "用户取消")
    
    def test_get_active_sessions(self):
        """测试获取活跃会话"""
        # 创建多个会话
        sessions = []
        for i in range(3):
            interaction_data = InteractionData(
                interaction_type=InteractionType.CONFIRMATION,
                title=f"会话 {i+1}",
                message=f"这是第 {i+1} 个会话"
            )
            session = self.session_manager.create_session(interaction_data)
            sessions.append(session)
        
        # 获取活跃会话
        active_sessions = self.session_manager.get_active_sessions()
        
        self.assertEqual(len(active_sessions), 3)
        
        # 完成一个会话
        self.session_manager.complete_session(
            sessions[0].session_id,
            {"choice": "yes"},
            "test-user"
        )
        
        # 再次获取活跃会话
        active_sessions = self.session_manager.get_active_sessions()
        self.assertEqual(len(active_sessions), 2)
    
    def test_get_sessions_by_workflow(self):
        """测试根据工作流获取会话"""
        workflow_id = "test-workflow-123"
        
        # 创建属于同一工作流的会话
        for i in range(2):
            interaction_data = InteractionData(
                interaction_type=InteractionType.CONFIRMATION,
                title=f"工作流会话 {i+1}",
                message="工作流测试"
            )
            self.session_manager.create_session(
                interaction_data,
                workflow_id=workflow_id
            )
        
        # 创建属于其他工作流的会话
        other_interaction_data = InteractionData(
            interaction_type=InteractionType.SELECTION,
            title="其他工作流会话",
            message="其他工作流测试"
        )
        self.session_manager.create_session(
            other_interaction_data,
            workflow_id="other-workflow"
        )
        
        # 获取特定工作流的会话
        workflow_sessions = self.session_manager.get_sessions_by_workflow(workflow_id)
        
        self.assertEqual(len(workflow_sessions), 2)
        for session in workflow_sessions:
            self.assertEqual(session.workflow_id, workflow_id)
    
    def test_register_callback(self):
        """测试注册回调"""
        session_id = "test-session-callback"
        callback_called = False
        
        def test_callback(session):
            nonlocal callback_called
            callback_called = True
            self.assertEqual(session.session_id, session_id)
        
        # 注册回调
        self.session_manager.register_callback(session_id, test_callback)
        
        # 创建会话
        interaction_data = InteractionData(
            interaction_type=InteractionType.CONFIRMATION,
            title="回调测试",
            message="测试回调功能"
        )
        
        session = self.session_manager.create_session(interaction_data)
        session.session_id = session_id  # 设置特定ID
        self.session_manager.active_sessions[session_id] = session
        
        # 完成会话，应该触发回调
        self.session_manager.complete_session(
            session_id,
            {"choice": "yes"},
            "test-user"
        )
        
        self.assertTrue(callback_called)
    
    def test_get_statistics(self):
        """测试获取统计信息"""
        # 创建一些会话
        sessions = []
        for i in range(3):
            interaction_data = InteractionData(
                interaction_type=InteractionType.CONFIRMATION,
                title=f"统计测试会话 {i+1}",
                message="统计测试"
            )
            session = self.session_manager.create_session(interaction_data)
            sessions.append(session)
        
        # 完成一个会话
        self.session_manager.complete_session(
            sessions[0].session_id,
            {"choice": "yes"},
            "test-user"
        )
        
        # 取消一个会话
        self.session_manager.cancel_session(
            sessions[1].session_id,
            "测试取消"
        )
        
        # 获取统计信息
        stats = self.session_manager.get_statistics()
        
        self.assertEqual(stats['active_sessions'], 1)  # 只有一个活跃会话
        self.assertGreaterEqual(stats['total_sessions'], 3)  # 至少3个总会话


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)

