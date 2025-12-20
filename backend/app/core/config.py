from pydantic_settings import BaseSettings
from pathlib import Path
from dotenv import load_dotenv
import secrets

# Project root
BASE_DIR = Path(__file__).resolve().parents[3]

# Load .env if exists (for local dev)
load_dotenv(BASE_DIR / ".env")

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./enterprise.db"
    
    # Make SECRET_KEY required but provide a fallback random one for safety
    SECRET_KEY: str = secrets.token_hex(32)  # Auto-generate if not set
    
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    GROQ_API_KEY: str  # Required for chat
    
    # Optional for embeddings (you're using FastEmbed now, so not needed)
    OPENAI_API_KEY: str = ""

    class Config:
        env_file = BASE_DIR / ".env"
        extra = "ignore"

# Instantiate settings
settings = Settings()