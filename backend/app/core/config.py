from pydantic_settings import BaseSettings
from pathlib import Path
from dotenv import load_dotenv

# Project root
BASE_DIR = Path(__file__).resolve().parents[3]

# Explicitly load .env (stable on Windows + reload)
load_dotenv(BASE_DIR / ".env")

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./enterprise.db"
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    GROQ_API_KEY: str

    class Config:
        env_file = BASE_DIR / ".env"
        extra = "ignore"

settings = Settings()
