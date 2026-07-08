import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from backend/.env (e.g. GEMINI_API_KEY, DATABASE_URL)
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

class Settings:
    PROJECT_NAME: str = "Sahayak"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-key-change-this-in-production-123456789")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 1 week
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost/sahayak")
    
    # OpenAI & LLMs
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "mock-key")

settings = Settings()
