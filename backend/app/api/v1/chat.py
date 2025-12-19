from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.clients.vector_client import VectorStore
from app.core.config import settings
from groq import Groq
import logging
from sentence_transformers import SentenceTransformer

router = APIRouter(tags=["chat"])
logger = logging.getLogger(__name__)

# -------------------------
# CLIENTS (SAFE AT IMPORT)
# -------------------------
vector_store = VectorStore(collection_name="enterprise_knowledge")
groq_client = Groq(api_key=settings.GROQ_API_KEY)

# -------------------------
# LAZY EMBEDDER (CRITICAL FIX)
# -------------------------
_embedder = None

def get_embedder():
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer("all-MiniLM-L6-v2")
    return _embedder

# -------------------------
# TEST ENDPOINT
# -------------------------
@router.get("/test")
async def chat_test():
    return {
        "status": "chat endpoint is live",
        "model": "all-MiniLM-L6-v2"
    }

# -------------------------
# REQUEST MODEL
# -------------------------
class ChatRequest(BaseModel):
    query: str

# -------------------------
# CHAT ENDPOINT
# -------------------------
@router.post("/chat")
async def chat(request: ChatRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    try:
        embedder = get_embedder()

        query_embedding = embedder.encode(request.query).tolist()

        search_results = vector_store.search(query_embedding, limit=5)

        context_parts = []
        for result in search_results:
            payload = result.payload or {}
            text = payload.get("text", "")
            if text:
                context_parts.append(text)

        context = "\n\n".join(context_parts)
        if not context:
            context = "No relevant documents found in the uploaded documents."

        prompt = f"""
You are an expert assistant for Enterprise Knowledge.

Use only the following context to answer the question.
If the answer is not in the context, say you do not know.

Context:
{context}

Question:
{request.query}

Answer:
""".strip()

        completion = groq_client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )

        answer = completion.choices[0].message.content.strip()
        return {"answer": answer}

    except Exception as e:
        logger.exception("Chat error")
        raise HTTPException(status_code=500, detail=str(e))
