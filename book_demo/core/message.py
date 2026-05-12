"""消息系统"""

from datetime import datetime
from typing import Any, Dict, Literal, Optional
from pydantic import BaseModel

# 定义消息角色的类型，限制其取值
MessageRole = Literal["user", "assistant", "system", "tool"]

class Message(BaseModel):
    """
    Message is a message in the conversation.
    """
    role: MessageRole
    content: str
    timestamp: datetime = None
    metadata: Optional[Dict[str, Any]] = None

    def __init__(self, role: MessageRole, content: str, **kwargs):
        super().__init__(
            role=role,
            content=content,
            timestamp=kwargs.get("timestamp", datetime.now()),
            metadata=kwargs.get("metadata", {}),
        )

    def to_dict(self)->Dict[str, Any]:
        """
        转换为字典格式（OpenAI API格式）
        """
        return {
            "role": self.role,
            "content": self.content,
        }

    def __str__(self)->str:
        """
        转换为字符串格式
        """
        return f"[Message] [{self.role}]: { self.content}"