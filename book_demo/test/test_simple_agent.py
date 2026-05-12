from dotenv import load_dotenv

load_dotenv()

from book_demo.agents.simple_agent import SimpleAgent
from book_demo.core.llm import HelloAgentsLLM
from book_demo.core.config import Config
from book_demo.tools.registry import ToolRegistry


# 创建LLM实例
llm = HelloAgentsLLM()

# 测试1:基础对话Agent（无工具）
print("=== 测试1:基础对话 ===")
basic_agent = SimpleAgent(
    name="基础助手",
    llm=llm,
    system_prompt="你是一个友好的AI助手，请用简洁明了的方式回答问题。"
)

response1 = basic_agent.run("你好，请介绍一下自己")
print(f"基础对话响应: {response1}\n")