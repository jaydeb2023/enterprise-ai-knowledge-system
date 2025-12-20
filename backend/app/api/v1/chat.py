from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging

router = APIRouter()

logger = logging.getLogger(__name__)

class ChatRequest(BaseModel):
    query: str

@router.get("/test")
async def chat_test():
    return {"status": "chat router loaded"}

@router.post("")
async def chat(req: ChatRequest):
    try:
        from app.clients.vector_client import VectorStore
        from app.core.config import settings
        from groq import Groq

        if not settings.GROQ_API_KEY:
            raise RuntimeError("GROQ_API_KEY missing")

        return {"answer": "Chat endpoint is alive and stable"}

    except Exception as e:
        logger.exception("Chat error")
        raise HTTPException(status_code=500, detail=str(e))
