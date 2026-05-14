"""HelloAgents统一LLM接口 - 基于OpenAI原生API"""


import os
from typing import Dict, Iterator, List, Optional
from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 后续需要支持其他API，如ModelScope、DeepSeek等。

class HelloAgentsLLM:
    """
    HelloAgentsLLM is a wrapper for the HelloAgent LLM API.
    Args:
        model: The model to use.
        api_key: The API key to use.
        base_url: The base URL to use.
        timeout: The timeout to use.
        temperature: The temperature to use.
        max_tokens: The max tokens to use.
    
    先支持OpenAI的API，后续支持其他API。
    """
    def __init__(self, model: str = None, api_key: str = None, base_url: str = None, timeout: int = None, temperature: float = 0.7, max_tokens: int = None):
        print("初始化LLM", model, api_key, base_url, timeout, temperature, max_tokens);
        self.model = model or os.getenv("LLM_MODEL_ID")
        self.api_key = api_key or os.getenv("LLM_API_KEY")
        self.base_url = base_url or os.getenv("LLM_BASE_URL")
        self.timeout = timeout or int(os.getenv("LLM_TIMEOUT", 60))
        self.temperature = temperature
        self.max_tokens = max_tokens

        if not all([self.model, self.api_key, self.base_url]):
            raise ValueError("LLM_API_KEY 和 LLM_BASE_URL 必须同时提供")

        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url, timeout=self.timeout)

    def think(self, messages: list[dict[str, str]], temperature: Optional[float] = None) -> Iterator[str]:
        """
        思考给定的消息，并返回思考结果。
        Args:
            messages: 消息列表
            temperature: 温度参数，如果未提供则使用初始化时的值
        Returns:
            str: 思考结果
        """
        print(f"正在调用大模型进行思考${self.model}")
        print(f"思考消息: {messages}")
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                stream=True
            )
            # 处理流式响应
            print("开始处理流式响应")
            for chunk in response:
                # 某些服务在最后会返回仅包含 usage 的 chunk，choices 可能为空
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta
                content = (delta.content or "") if delta else ""
                if content:
                    yield content
            
        except Exception as e:
            print(f"Error: {e}")
            return f"Error: {e}"


    def invoke(self, messages: list[dict[str, str]], **kwargs) -> str:
        """
        调用大模型，并返回响应。
        Args:
            messages: 消息列表
            temperature: 温度参数，如果未提供则使用初始化时的值
        Returns:
            str: 响应
        """
        try:
            print("<<<<<<<")
            print( messages, kwargs);
            print("<<<<<<<")
            response = self.client.chat.completions.create(
                model= self.model,
                messages=messages,
                temperature=kwargs.get('temperature', self.temperature),
                max_tokens=kwargs.get('max_tokens', self.max_tokens),
                **{k: v for k, v in kwargs.items() if k not in ['temperature', 'max_tokens']}
            )
            result = response.choices[0].message.content
            print(">>>>>>>");
            print(result);
            print(">>>>>>>");
            return result
        except Exception as e:
            raise Exception(f"LLM调用失败: {str(e)}")

    def stream_invoke(self, messages: list[dict[str, str]], **kwargs) -> Iterator[str]:
        """
        流式调用大模型，并返回响应。
        Args:
            messages: 消息列表
            **kwargs: 其他参数
        Returns:
            Iterator[str]: 响应
        """
        temperature = kwargs.get('temperature')
        yield from self.think(messages, temperature)
        