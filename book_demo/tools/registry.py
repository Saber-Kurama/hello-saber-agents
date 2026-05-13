"""工具注册表 原生工具系统"""

from typing import Any, Callable
from .base import Tool


class ToolRegistry:
    """
    工具注册表
    提供工具的注册、管理和执行功能。
    """
    def __init__(self):
        self._tools: dict[str, Tool] = {}
        self._functions: dict[str, dict[str, Any]] = {}

    def register_tool(self, tool: Tool):
        """注册 Tool 对象"""
        if tool.name in self._tools:
            raise ValueError(f"工具 '{tool.name}' 已存在")
        self._tools[tool.name] = tool
        print(f"✅ 工具 '{tool.name}' 已注册。")

    def unregister_tool(self, tool_name: str):
        """注销 Tool 对象"""
        if tool_name not in self._tools:
            raise ValueError(f"工具 '{tool_name}' 不存在")
        del self._tools[tool_name]
        print(f"✅ 工具 '{tool_name}' 已注销。")

    def register_function(self, name: str, description: str, func: Callable[[str], str]):
        """注册函数
        Args:
            name: 函数名称
            description: 函数描述
            function: 函数
        """
        if name in self._functions:
            raise ValueError(f"函数 '{name}' 已存在")
        self._functions[name] = {
            "description": description,
            "func": func
        }
        print(f"✅ 函数 '{name}' 已注册。")

    def unregister_function(self, name: str):
        """注销函数"""
        if name not in self._functions:
            raise ValueError(f"函数 '{name}' 不存在")
        del self._functions[name]
        print(f"✅ 函数 '{name}' 已注销。")

    def get_tools_description(self) -> str:
        """获取所有可用工具的格式化描述字符串"""
        descriptions = []

        # Tool对象描述
        for tool in self._tools.values():
            descriptions.append(f"- {tool.name}: {tool.description}")

        # 函数工具描述
        for name, info in self._functions.items():
            descriptions.append(f"- {name}: {info['description']}")

        return "\n".join(descriptions) if descriptions else "暂无可用工具"
    

    def list_tools(self) -> list[Tool]:
        """获取所有可用工具"""
        return list(self._tools.keys()) + list(self._functions.keys())
    
    
    def get_all_tools(self) -> list[Tool]:
        """获取所有可用工具"""
        return list(self._tools.values())


    def clear(self):
        """清空所有工具和函数"""
        self._tools.clear()
        self._functions.clear()