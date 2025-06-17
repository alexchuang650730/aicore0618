"""
Human-in-the-Loop MCP 数据模型
定义交互会话和相关数据结构
"""

import json
import uuid
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional, Union


class InteractionType(Enum):
    """交互类型枚举"""
    CONFIRMATION = "confirmation"
    SELECTION = "selection"
    TEXT_INPUT = "text_input"
    FILE_UPLOAD = "file_upload"
    CUSTOM = "custom"


class SessionStatus(Enum):
    """会话状态枚举"""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"
    ERROR = "error"


@dataclass
class InteractionField:
    """交互字段定义"""
    name: str
    label: str
    field_type: str = "text"
    required: bool = False
    default: Any = None
    validation: Optional[str] = None
    options: Optional[List[Dict[str, Any]]] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    
    def to_dict(self):
        return asdict(self)


@dataclass
class InteractionData:
    """交互数据定义"""
    interaction_type: InteractionType
    title: str
    message: str
    fields: Optional[List[InteractionField]] = None
    options: Optional[List[Dict[str, Any]]] = None
    default_value: Any = None
    timeout: int = 300
    multiple: bool = False
    accept_types: Optional[List[str]] = None
    max_file_size: Optional[str] = None
    
    def to_dict(self):
        result = asdict(self)
        result['interaction_type'] = self.interaction_type.value
        if self.fields:
            result['fields'] = [field.to_dict() for field in self.fields]
        return result


@dataclass
class UserResponse:
    """用户响应数据"""
    session_id: str
    response_data: Dict[str, Any]
    submitted_at: datetime
    user_id: Optional[str] = None
    
    def to_dict(self):
        result = asdict(self)
        result['submitted_at'] = self.submitted_at.isoformat()
        return result


class InteractionSession:
    """交互会话类"""
    
    def __init__(self, session_id: str = None, interaction_data: InteractionData = None,
                 workflow_id: str = None, callback_url: str = None):
        self.session_id = session_id or str(uuid.uuid4())
        self.interaction_data = interaction_data
        self.workflow_id = workflow_id
        self.callback_url = callback_url
        self.status = SessionStatus.PENDING
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.expires_at = datetime.now() + timedelta(seconds=interaction_data.timeout if interaction_data else 300)
        self.response: Optional[UserResponse] = None
        self.error_message: Optional[str] = None
        
    def update_status(self, status: SessionStatus, error_message: str = None):
        """更新会话状态"""
        self.status = status
        self.updated_at = datetime.now()
        if error_message:
            self.error_message = error_message
    
    def set_response(self, response_data: Dict[str, Any], user_id: str = None):
        """设置用户响应"""
        self.response = UserResponse(
            session_id=self.session_id,
            response_data=response_data,
            submitted_at=datetime.now(),
            user_id=user_id
        )
        self.update_status(SessionStatus.COMPLETED)
    
    def is_expired(self) -> bool:
        """检查会话是否已过期"""
        return datetime.now() > self.expires_at
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = {
            'session_id': self.session_id,
            'workflow_id': self.workflow_id,
            'callback_url': self.callback_url,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'expires_at': self.expires_at.isoformat(),
            'error_message': self.error_message
        }
        
        if self.interaction_data:
            result['interaction_data'] = self.interaction_data.to_dict()
        
        if self.response:
            result['response'] = self.response.to_dict()
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InteractionSession':
        """从字典创建会话对象"""
        session = cls()
        session.session_id = data['session_id']
        session.workflow_id = data.get('workflow_id')
        session.callback_url = data.get('callback_url')
        session.status = SessionStatus(data['status'])
        session.created_at = datetime.fromisoformat(data['created_at'])
        session.updated_at = datetime.fromisoformat(data['updated_at'])
        session.expires_at = datetime.fromisoformat(data['expires_at'])
        session.error_message = data.get('error_message')
        
        if 'interaction_data' in data:
            interaction_data = data['interaction_data']
            fields = None
            if 'fields' in interaction_data and interaction_data['fields']:
                fields = [InteractionField(**field) for field in interaction_data['fields']]
            
            session.interaction_data = InteractionData(
                interaction_type=InteractionType(interaction_data['interaction_type']),
                title=interaction_data['title'],
                message=interaction_data['message'],
                fields=fields,
                options=interaction_data.get('options'),
                default_value=interaction_data.get('default_value'),
                timeout=interaction_data.get('timeout', 300),
                multiple=interaction_data.get('multiple', False),
                accept_types=interaction_data.get('accept_types'),
                max_file_size=interaction_data.get('max_file_size')
            )
        
        if 'response' in data and data['response']:
            response_data = data['response']
            session.response = UserResponse(
                session_id=response_data['session_id'],
                response_data=response_data['response_data'],
                submitted_at=datetime.fromisoformat(response_data['submitted_at']),
                user_id=response_data.get('user_id')
            )
        
        return session


# 预定义的交互模板
class InteractionTemplates:
    """预定义的交互模板"""
    
    @staticmethod
    def confirmation(title: str, message: str, timeout: int = 300) -> InteractionData:
        """确认对话框模板"""
        return InteractionData(
            interaction_type=InteractionType.CONFIRMATION,
            title=title,
            message=message,
            options=[
                {"value": "confirm", "label": "确认"},
                {"value": "cancel", "label": "取消"}
            ],
            default_value="cancel",
            timeout=timeout
        )
    
    @staticmethod
    def selection(title: str, message: str, options: List[Dict[str, Any]], 
                 multiple: bool = False, timeout: int = 600) -> InteractionData:
        """选择对话框模板"""
        return InteractionData(
            interaction_type=InteractionType.SELECTION,
            title=title,
            message=message,
            options=options,
            multiple=multiple,
            timeout=timeout
        )
    
    @staticmethod
    def text_input(title: str, message: str, fields: List[InteractionField], 
                  timeout: int = 900) -> InteractionData:
        """文本输入模板"""
        return InteractionData(
            interaction_type=InteractionType.TEXT_INPUT,
            title=title,
            message=message,
            fields=fields,
            timeout=timeout
        )
    
    @staticmethod
    def file_upload(title: str, message: str, accept_types: List[str] = None,
                   max_file_size: str = "10MB", multiple: bool = False,
                   timeout: int = 1200) -> InteractionData:
        """文件上传模板"""
        return InteractionData(
            interaction_type=InteractionType.FILE_UPLOAD,
            title=title,
            message=message,
            accept_types=accept_types or [".json", ".yaml", ".yml", ".txt"],
            max_file_size=max_file_size,
            multiple=multiple,
            timeout=timeout
        )


# 常用的交互字段
class CommonFields:
    """常用的交互字段定义"""
    
    @staticmethod
    def text_field(name: str, label: str, required: bool = False, 
                  default: str = None, validation: str = None) -> InteractionField:
        """文本字段"""
        return InteractionField(
            name=name,
            label=label,
            field_type="text",
            required=required,
            default=default,
            validation=validation
        )
    
    @staticmethod
    def number_field(name: str, label: str, required: bool = False,
                    default: Union[int, float] = None, min_value: Union[int, float] = None,
                    max_value: Union[int, float] = None) -> InteractionField:
        """数字字段"""
        return InteractionField(
            name=name,
            label=label,
            field_type="number",
            required=required,
            default=default,
            min_value=min_value,
            max_value=max_value
        )
    
    @staticmethod
    def email_field(name: str, label: str, required: bool = False) -> InteractionField:
        """邮箱字段"""
        return InteractionField(
            name=name,
            label=label,
            field_type="email",
            required=required,
            validation=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        )
    
    @staticmethod
    def url_field(name: str, label: str, required: bool = False) -> InteractionField:
        """URL字段"""
        return InteractionField(
            name=name,
            label=label,
            field_type="url",
            required=required,
            validation=r"^https?://.*"
        )
    
    @staticmethod
    def select_field(name: str, label: str, options: List[Dict[str, Any]],
                    required: bool = False, default: str = None) -> InteractionField:
        """选择字段"""
        return InteractionField(
            name=name,
            label=label,
            field_type="select",
            required=required,
            default=default,
            options=options
        )

