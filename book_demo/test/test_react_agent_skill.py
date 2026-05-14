from dotenv import load_dotenv
from book_demo.tools.builtin.calculator import CalculatorTool
from book_demo.tools.builtin.skill_tool import SkillTool

load_dotenv()

from book_demo.agents.react_agent import ReActAgent
from book_demo.core.llm import HelloAgentsLLM
from book_demo.core.config import Config
from book_demo.tools.registry import ToolRegistry


# 创建LLM实例
llm = HelloAgentsLLM("gpt-4o-mini")

tool_registry = ToolRegistry()
calculator = CalculatorTool()
skill = SkillTool()
tool_registry.register_tool(calculator)
tool_registry.register_tool(skill)

# 测试1:基础对话Agent（无工具）
print("=== 测试1:基础对话 ===")
basic_agent = ReActAgent(
    name="基础助手",
    llm=llm,
    tool_registry=tool_registry,
    system_prompt="你是一个友好的AI助手，请用简洁明了的方式回答问题。"
)

# response1 = basic_agent.run("你好，请介绍一下自己")
# print(f"基础对话响应: {response1}\n")

response2 = basic_agent.run("请先加载 test-skill 技能，再告诉我该怎么写单元测试。")
print(f"基础对话响应: {response2}\n")