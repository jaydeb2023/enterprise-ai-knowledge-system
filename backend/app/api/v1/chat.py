from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.clients.vector_client import VectorStore
from app.core.config import settings
from groq import Groq
import logging

router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)

logger = logging.getLogger(__name__)

# -------------------------
# SAFE AT IMPORT
# -------------------------
vector_store = VectorStore(collection_name="enterprise_knowledge")

# -------------------------
# GROQ CLIENT (LAZY)
# -------------------------
_groq_client = None

def get_groq_client():
    global _groq_client
    if _groq_client is None:
        if not settings.GROQ_API_KEY:
            raise RuntimeError("GROQ_API_KEY is not set")
        _groq_client = Groq(api_key=settings.GROQ_API_KEY)
    return _groq_client

# -------------------------
# EMBEDDING USING GROQ
# -------------------------
def embed_text(text: str) -> list[float]:
    client = get_groq_client()
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=[text],
    )
    return response.data[0].embedding

# -------------------------
# TEST ENDPOINT
# -------------------------
@router.get("/test")
async def chat_test():
    return {"chat_service": "ok"}

# -------------------------
# REQUEST MODEL
# -------------------------
class ChatRequest(BaseModel):
    query: str

# -------------------------
# CHAT ENDPOINT
# -------------------------
@router.post("")
async def chat(request: ChatRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    try:
        query_embedding = embed_text(request.query)
        results = vector_store.search(query_embedding, limit=5)

        context_parts = []
        for r in results:
            payload = r.payload or {}
            text = payload.get("text", "")
            if text:
                context_parts.append(text)

        context = "\n\n".join(context_parts) or "No relevant documents found."

        prompt = f"""
Use ONLY the context below to answer.
If the answer is not present, say you do not know.

Context:
{context}

Question:
{request.query}

Answer:
""".strip()

        client = get_groq_client()
        completion = client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )

        return {"answer": completion.choices[0].message.content.strip()}

    except Exception as e:
        logger.exception("Chat error")
        raise HTTPException(status_code=500, detail=str(e))
