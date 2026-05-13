"""ReAct Agent实现 - 推理与行动结合的智能体"""

# 默认ReAct提示词模板
from os import curdir
import re
from typing import Optional, Tuple

from book_demo.tools.registry import ToolRegistry
from book_demo.core.agent import Agent
from book_demo.core.config import Config
from book_demo.core.llm import HelloAgentsLLM
from book_demo.core.message import Message


DEFALUT_REACT_PROMPT = """你是一个具备推理和行动能力的AI助手。你可以通过思考分析问题，然后调用合适的工具来获取信息，最终给出准确的答案。

## 可用工具
{tools}

## 工作流程
请严格按照以下格式进行回应，每次只能执行一个步骤:

Thought: 分析当前问题，思考需要什么信息或采取什么行动。
Action: 选择一个行动，格式必须是以下之一:
- `{{tool_name}}[{{tool_input}}]` - 调用指定工具
- `Finish[最终答案]` - 当你有足够信息给出最终答案时

## 重要提醒
1. 每次回应必须包含Thought和Action两部分
2. 工具调用的格式必须严格遵循:工具名[参数]
3. 只有当你确信有足够信息回答问题时，才使用Finish
4. 如果工具返回的信息不够，继续使用其他工具或相同工具的不同参数

## 当前任务
**Question:** {question}

## 执行历史
{history}

现在开始你的推理和行动:
"""

class ReActAgent(Agent):
    """
    ReActAgent is a wrapper for the ReAct agent.
    ReAct (Reasoning and Acting) Agent
    
    结合推理和行动的智能体，能够：
    1. 分析问题并制定行动计划
    2. 调用外部工具获取信息
    3. 基于观察结果进行推理
    4. 迭代执行直到得出最终答案
    
    这是一个经典的Agent范式，特别适合需要外部信息的任务。
    """
    def __init__(
        self, 
        name: str, llm: HelloAgentsLLM,
        tool_registry: Optional[ToolRegistry] = None,
        system_prompt: Optional[str] = None,
        config: Optional[Config] = None,
        max_steps: int = 5,
        custom_prompt: Optional[str] = None
    ):
        super().__init__(name, llm, system_prompt, config)
        self.tool_registry = tool_registry
        self.max_steps = max_steps
        self.current_history: list[str] = []
        self.prompt_template = custom_prompt if custom_prompt else DEFALUT_REACT_PROMPT
        print(f"✅ {name} 初始化完成，最大步数: {self.max_steps}")

    def run(self, input_text: str, **kwargs) -> str:
        """运行Agent"""
        self.current_history = []
        current_step = 0

        while current_step < self.max_steps:
            current_step += 1
            print(f"\n--- 第 {current_step} 步 ---")

            # 构建提示词

            tool_desc = self.tool_registry.get_tools_description()
            history_str = "\n".join(self.current_history)
            prompt = self.prompt_template.format(
                tools=tool_desc,
                question=input_text,
                history=history_str
            )

            

            # 调用LLM
            messages = [{"role": "user", "content": prompt}]
            response_text = self.llm.invoke(messages, **kwargs)

            # 解析响应
            thought, action = self._parse_response(response_text)

            print(f"💡 思考: {thought}")
            print(f"🔧 行动: {action}")
            # 检查完成条件
            if action and action.startswith("Finish["):
                final_answer = self._parse_action_input(action)
                self.add_message(Message('user', input_text))
                self.add_message(Message('assistant', final_answer))
                print(f"✅ {self.name} 完成任务")
                return final_answer
            
            # 工具调用
            if action:
                tool_name, tool_input = self._parse_action(action)
                print(f"🔧 工具调用: {tool_name}, {tool_input}")
                observation = self.tool_registry.execute_tool(tool_name, tool_input)
                print(f"🔧 工具执行结果: {observation}")
                self.current_history.append(f"Action: {action}")
                self.current_history.append(f"Observation: {observation}")

            
        # 超出最大步数，返回最终答案
        final_answer = "抱歉，我无法在限定步数内完成这个任务。"
        self.add_message(Message('user', input_text))
        self.add_message(Message('assistant', final_answer))
        print(f"❌ {self.name} 超出最大步数，返回最终答案: {final_answer}")
        return final_answer

    def _parse_response(self, text: str) -> tuple[str, str]:
        """解析响应
        
        解析LLM输出，提取思考和行动。

        兼容常见变体：
        - Thought/Action 的全角冒号（：）
        - 中文标签：思考/行动
        - Markdown 强调：**Thought:** / **Action:**
        """
        t = (text or "").strip()
        
        m = re.search(
            r"(?:\*\*)?(Thought|思考)(?:\*\*)?\s*[:：]\s*(.*?)\n(?:\*\*)?(Action|行动)(?:\*\*)?\s*[:：]\s*(.*)\s*$",
            t,
            flags=re.DOTALL,
        )

        if m:
            thought = m.group(2).strip()
            action = m.group(4).strip()
            return thought, action
        
        # Fallback: find first Thought-like line and first Action-like line anywhere
        thought_match = re.search(r"(?:\*\*)?(Thought|思考)(?:\*\*)?\s*[:：]\s*(.*)", t)
        action_match = re.search(r"(?:\*\*)?(Action|行动)(?:\*\*)?\s*[:：]\s*(.*)", t)
        thought = thought_match.group(2).strip() if thought_match else None
        action_raw = action_match.group(2).strip() if action_match else None

        # 关键修复：如果 action 中包含另一个 Thought/Action/Observation，截断到该位置
        # 防止模型一次输出多个 Thought/Action 循环时，把后续内容都当作第一个 Action 的输入
        if action_raw:
            stop_patterns = [
                r"\nThought:", r"\n思考:", r"\nAction:", r"\n行动:",
                r"\nObservation:", r"\n观察:", r"\n\*\*Thought", r"\n\*\*Action",
            ]
            earliest_stop = len(action_raw)
            for pat in stop_patterns:
                m = re.search(pat, action_raw, re.IGNORECASE)
                if m and m.start() < earliest_stop:
                    earliest_stop = m.start()
            action_raw = action_raw[:earliest_stop].strip()
        
        return thought, action_raw
    

    def _parse_action(self, action_text: str) -> Tuple[Optional[str], Optional[str]]:
        """解析行动文本，提取工具名称和输入
        
        使用括号匹配算法而非贪婪正则，正确处理嵌套 JSON。
        """
        # 先找工具名
        name_match = re.match(r"(\w+)\[", action_text)
        if not name_match:
            return None, None
        
        tool_name = name_match.group(1)
        start = name_match.end() - 1  # '[' 的位置
        
        # 使用括号匹配找到对应的 ']'
        depth = 0
        in_string = False
        escape = False
        end_pos = None
        
        for i, c in enumerate(action_text[start:], start):
            if escape:
                escape = False
                continue
            if c == '\\' and in_string:
                escape = True
                continue
            if c == '"' and not escape:
                in_string = not in_string
                continue
            if in_string:
                continue
            if c == '[':
                depth += 1
            elif c == ']':
                depth -= 1
                if depth == 0:
                    end_pos = i
                    break
        
        if end_pos is not None:
            tool_input = action_text[start + 1:end_pos]
            return tool_name, tool_input
        
        # fallback: 如果括号不匹配，尝试简单正则（不跨行）
        # 注意：不使用 re.DOTALL，这样 . 不会匹配换行符
        match = re.match(r"(\w+)\[([^\n]*)\]", action_text)
        if match:
            return match.group(1), match.group(2)
        
        return None, None
    
    def _parse_action_input(self, action_text: str) -> str:
        """解析行动输入

        兼容多种 Finish 书写：
        - Finish[...]
        - Finish：... / Finish: ...（无方括号）
        - Finish\n<content>（换行后直接给内容/补丁）
        """
        # 规范格式：Finish[...]
        match = re.match(r"\w+\[(.*)\]\s*$", action_text, flags=re.DOTALL)
        if match:
            return match.group(1)

        # 宽松格式：Finish: ... 或 Finish：...
        m2 = re.match(r"finish\s*[:：]\s*(.*)", action_text, flags=re.IGNORECASE | re.DOTALL)
        if m2:
            return m2.group(1)

        # 再宽松：去掉前缀 "Finish" 后的剩余内容
        if action_text.lower().startswith("finish"):
            return action_text[len("finish"):].strip()

        return ""