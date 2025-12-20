from pydantic_settings import BaseSettings
from pathlib import Path
from dotenv import load_dotenv

# Project root (adjust if your structure changes)
BASE_DIR = Path(__file__).resolve().parents[3]

# Load .env file explicitly (helps on all OS, including Windows)
load_dotenv(BASE_DIR / ".env")

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./enterprise.db"
    SECRET_KEY: str  # Required – generate a strong one if missing
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    GROQ_API_KEY: str  # For chat/inference (Llama, Mixtral, etc.)
    OPENAI_API_KEY: str = ""  # Add this for embeddings (optional if using alternative)

    # Optional: Fallback to HuggingFace if no OpenAI key (set to model name)
    # EMBEDDING_PROVIDER: str = "openai"  # or "huggingface"

    class Config:
        env_file = BASE_DIR / ".env"
        extra = "ignore"

settings = Settings()