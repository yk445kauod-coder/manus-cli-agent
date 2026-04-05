import os

class Config:
    # استخدام OpenAI-compatible API (مثل Groq أو غيرها من الخدمات المجانية)
    # ملاحظة: Manus يوفر OPENAI_API_KEY مسبقاً للوصول لنماذج مثل gpt-4.1-mini
    API_KEY = os.getenv("OPENAI_API_KEY")
    BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    MODEL = "gpt-4.1-mini" # نموذج سريع وذكي متاح في Manus
    
    # إعدادات النظام
    SKILLS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src/skills")
    MCP_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "src/mcp")
    
    # معلومات المطور
    DEVELOPER = "Yousef Khamis"
    PROJECT_NAME = "Manus CLI Agent"
