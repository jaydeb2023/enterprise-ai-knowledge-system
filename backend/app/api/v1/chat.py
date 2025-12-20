from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging

router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)

logger = logging.getLogger(__name__)

# ---------- REQUEST MODEL ----------
class ChatRequest(BaseModel):
    query: str

# ---------- SAFE TEST ----------
@router.get("/test")
async def chat_test():
    return {"status": "chat router loaded"}

# ---------- CHAT ----------
@router.post("")
async def chat(req: ChatRequest):
    try:
        # Lazy imports (CRITICAL)
        from app.clients.vector_client import VectorStore
        from app.core.config import settings
        from groq import Groq

        if not settings.GROQ_API_KEY:
            raise RuntimeError("GROQ_API_KEY missing")

        vector_store = VectorStore(collection_name="enterprise_knowledge")
        client = Groq(api_key=settings.GROQ_API_KEY)

        # TEMP RESPONSE (we’ll add embeddings later)
        return {"answer": "Chat endpoint is alive and stable"}

    except Exception as e:
        logger.exception("Chat error")
        raise HTTPException(status_code=500, detail=str(e))
