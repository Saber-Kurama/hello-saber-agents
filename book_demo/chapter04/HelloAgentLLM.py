import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import List, Dict, Optional

# from serpapi import SerpApiClient

load_dotenv()


class HelloAgentsLLM:
    def __init__(self, model: str = None, api_key: str = None, base_url: str = None, timeout: int = None):
        """
        初始化客户端。优先使用传入参数，如果未提供，则从环境变量加载。
        """
        self.model = model or os.getenv("LLM_MODEL_ID")
        apiKey = api_key or os.getenv("LLM_API_KEY")
        baseUrl = base_url or os.getenv("LLM_BASE_URL")
        timeout = timeout or int(os.getenv("LLM_TIMEOUT", 60))
        
        if not all([self.model, apiKey, baseUrl]):
            raise ValueError("LLM_API_KEY 和 LLM_BASE_URL 必须同时提供")
        
        self.client = OpenAI(api_key=apiKey, base_url=baseUrl, timeout=timeout)


    def think(self, messages: list[dict[str, str]], temperature: Optional[float] = None) -> str:
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
            collected_chunks = []
            for chunk in response:
                # 某些服务在最后会返回仅包含 usage 的 chunk，choices 可能为空
                if not chunk.choices:
                    continue

                delta = chunk.choices[0].delta
                content = (delta.content or "") if delta else ""
                if content:
                    collected_chunks.append(content)
            full_response = "".join(collected_chunks)
            print(f"完整响应: {full_response}")
            return full_response
        except Exception as e:
            print(f"Error: {e}")
            return f"Error: {e}"


# def search(query: str) -> str:
#     """
#     一个基于SerpApi的实战网页搜索引擎工具。
#     它会智能地解析搜索结果，优先返回直接答案或知识图谱信息。
#     """
#     print(f"🔍 正在执行 [SerpApi] 网页搜索: {query}")
#     try:
#         api_key = os.getenv("SERPAPI_API_KEY")
#         if not api_key:
#             return "错误:未配置SERPAPI_API_KEY环境变量。"
#         params = {
#             "engine": "google",
#             "q": query,
#             "api_key": api_key,
#             "gl": "cn",  # 国家代码
#             "hl": "zh-cn", # 语言代码
#         }
#         client = SerpApiClient(params)
#         results = client.get_dict()
#         # 智能解析:优先寻找最直接的答案
#         print(f"🔍 搜索结果: {results}")
#         if "answer_box_list" in results:
#             return "\n".join(results["answer_box_list"])
#         if "answer_box" in results and "answer" in results["answer_box"]:
#             return results["answer_box"]["answer"]
#         if "knowledge_graph" in results and "description" in results["knowledge_graph"]:
#             return results["knowledge_graph"]["description"]
#         if "organic_results" in results and results["organic_results"]:
#             # 如果没有直接答案，则返回前三个有机结果的摘要
#             snippets = [
#                 f"[{i+1}] {res.get('title', '')}\n{res.get('snippet', '')}"
#                 for i, res in enumerate(results["organic_results"][:3])
#             ]
#             return "\n\n".join(snippets)
        
#         return f"对不起，没有找到关于 '{query}' 的信息。"
#     except Exception as e:
#         print(f"🚨 搜索失败: {e}")
#         return f"Error: {e}"
