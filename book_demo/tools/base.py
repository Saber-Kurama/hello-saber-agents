"""工具基类"""


from abc import ABC, abstractmethod
from typing import Any, Dict, List

from pydantic import BaseModel


class ToolParameter(BaseModel):
    """工具参数基类"""
    name: str
    description: str
    type: str
    required: bool = True
    default: Any = None
   
class Tool(ABC):
    """工具基类"""
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def run(self, parameters: Dict[str, Any]) -> str:
        """运行工具"""
        pass

    @abstractmethod
    def get_parameters(self) -> List[ToolParameter]:
        """获取工具参数"""
        pass