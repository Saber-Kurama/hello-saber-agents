"""
ContextBuilder 与 Agent 集成示例

展示如何将 ContextBuilder 集成到 Agent 中，实现：
1. 上下文感知的 Agent
2. 自动构建优化的上下文
3. 记忆管理与上下文构建的协同
"""
from typing import Optional
from dotenv import load_dotenv
import os
load_dotenv()
from hello_agents import SimpleAgent, HelloAgentsLLM, ToolRegistry
from hello_agents.context import ContextBuilder, ContextConfig


class ContextAwareAgent(SimpleAgent):
    """
    ContextAwareAgent 是一个上下文感知的 Agent，它使用 ContextBuilder 构建优化的上下文。
    """
    def __init__(self, name: str, llm: HelloAgentsLLM, **kwargs):
        super().__init__(name, llm, **kwargs)
        self.context_builder = ContextBuilder(config=ContextConfig(max_tokens=3000))
        self.conversation_history = []

    def run(self, user_input: str) -> str:
        """重写的运行方法 - 实现上下文感知的对话逻辑"""
        print(f"🤖 {self.name} 正在处理: {user_input}")
        
        # 构建上下文
        context = self.context_builder.build(user_input, self.conversation_history)
        print(f"🔍 构建的上下文: {context}")
        
        # 构建消息列表
        messages = [
            {"role": "system", "content": context},
            {"role": "user", "content": user_input}
        ]
        response = self.llm.invoke(messages)
        return response