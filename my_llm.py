import os
from typing import Optional
from openai import OpenAI
from HelloAgentLLM import HelloAgentLLM

class MyLLM(HelloAgentLLM):
    """
    一个自定义的LLM客户端，通过继承增加了对ModelScope的支持。
    """
    pass # 暂时留空