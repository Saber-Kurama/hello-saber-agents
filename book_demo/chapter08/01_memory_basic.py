from hello_agents import SimpleAgent, HelloAgentsLLM, ToolRegistry
from hello_agents.tools import MemoryTool, RAGTool
from dotenv import load_dotenv
import os
load_dotenv()

print(os.getenv("LLM_API_KEY"))
print(os.getenv("LLM_BASE_URL"))

llm = HelloAgentsLLM( "gpt-4o-mini",  os.getenv("LLM_API_KEY"), os.getenv("LLM_BASE_URL"))

system_prompt="""你是一个必须使用 memory 工具的助手。
规则：
1. 用户要求记住信息时，必须先调用：[TOOL_CALL:memory:action=add,content=要记住的内容]
2. 用户询问过往信息时，必须先调用：[TOOL_CALL:memory:action=search,query=检索关键词]
3. 禁止在未调用工具的情况下声称已记住或已查询记忆。
4. 收到工具结果后再组织最终回答。"""



agent = SimpleAgent(
    name="Memory Agent",
    llm=llm,
    tool_registry=ToolRegistry(),
    system_prompt="你是助手。回答时优先依据「相关记忆」中的事实，不要编造。",
)

# 创建工具注册表
tool_registry = ToolRegistry()
# 添加记忆工具
memory_tool = MemoryTool(user_id="user_123")
tool_registry.register_tool(memory_tool)
rag_tool = RAGTool(user_id="user_123")
tool_registry.register_tool(rag_tool)

agent.tool_registry = tool_registry

def remember(content: str, importance: float = 0.9) -> str:
    """写入语义记忆（持久化，适合用户画像、偏好等事实）"""
    return memory_tool.run({
        "action": "add",
        "content": content,
        "memory_type": "semantic",
        "importance": importance,
    })


def recall(query: str, limit: int = 5) -> str:
    """检索记忆，返回格式化文本"""
    return memory_tool.run({
        "action": "search",
        "query": query,
        "limit": limit,
    })


def run_with_memory(user_input: str) -> str:
    """稳妥流程：先 search → 注入 prompt → 再让 LLM 回答"""
    memory_context = memory_tool.get_context_for_query(user_input, limit=5)

    if memory_context:
        augmented = (
            f"{memory_context}\n\n"
            f"用户问题：{user_input}\n"
            "请仅根据上述记忆和当前问题回答；若记忆中没有相关信息，请明确说不知道。"
        )
    else:
        augmented = user_input

    return agent.run(augmented)


# --- 演示 ---

# 开始对话
response = agent.run("你好！请记住我叫张三，我是一名Python开发者")
print(response)
response = agent.run("你还记得我叫什么吗？我的职业是什么？")
print(response)

# # 2. 清空对话历史，证明第二轮靠的是 memory 而不是 chat history
# agent.clear_history()

# response = run_with_memory("你还记得我叫什么吗？我的职业是什么？")
# print(response)
