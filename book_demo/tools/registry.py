"""工具注册表 原生工具系统"""

from typing import Any
from hello_agents.tools import Tool


class ToolRegistry:
    """
    工具注册表
    提供工具的注册、管理和执行功能。
    """
    def __init__(self):
        self._tools: dict[str, Tool] = {}
        self._functions: dict[str, dict[str, Any]] = {}

    def register_tool(self, tool: Tool):
        """注册工具"""
        self._tools[tool.name] = tool
        print(f"✅ 工具 '{tool.name}' 已注册。")