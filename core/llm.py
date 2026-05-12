from openai import OpenAI


class HelloAgentLLM:
    """
    HelloAgentLLM is a wrapper for the HelloAgent LLM API.
    """
    def __init__(
        self, model: str = None, 
        api_key: str = None, 
        base_url: str = None, 
        temperature: float = 0.7,
        max_tokens: int = None,
        timeout: int = None):
        self.model = model
        self.api_key = api_key
        self.base_url = base_url
        self.temperature = temperature
        self.timeout = timeout
        self.max_tokens = max_tokens

        if not all([self.model, self.api_key, self.base_url]):
            raise ValueError("LLM_API_KEY 和 LLM_BASE_URL 必须同时提供")
        
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url, timeout=self.timeout)

    def get_response(self, prompt: str) -> str:
        return self.model.generate(prompt)