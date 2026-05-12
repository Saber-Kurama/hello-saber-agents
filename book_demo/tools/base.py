"""工具基类"""


from abc import ABC, abstractmethod


class Tool(ABC):
    """工具基类"""
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def run(self, input: str) -> str:
        """运行工具"""
        pass