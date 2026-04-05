import openai
from src.config import Config

class LLMEngine:
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=Config.API_KEY,
            base_url=Config.BASE_URL
        )
        self.model = Config.MODEL

    def chat(self, messages, tools=None, tool_choice="auto"):
        """
        إرسال طلب إلى نموذج اللغة مع دعم الأدوات.
        """
        params = {
            "model": self.model,
            "messages": messages,
        }
        
        if tools:
            params["tools"] = tools
            params["tool_choice"] = tool_choice
            
        try:
            response = self.client.chat.completions.create(**params)
            return response
        except Exception as e:
            print(f"Error in LLM request: {e}")
            return None

    def stream_chat(self, messages):
        """
        إرسال طلب مع تدفق (Streaming) للاستجابة السريعة.
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True
            )
            return response
        except Exception as e:
            print(f"Error in streaming LLM request: {e}")
            return None
