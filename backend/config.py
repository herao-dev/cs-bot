import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "faq-bot-2026")
    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    DEEPSEEK_MODEL = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
    CHROMA_DIR = os.path.join(os.path.dirname(__file__), "data", "chroma")
    UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "data", "uploads")
    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 80
    MAX_HISTORY = 20
    TOP_K = 5
