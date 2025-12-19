from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.clients.vector_client import VectorStore
from app.core.config import settings
from groq import Groq
import logging
from sentence_transformers import SentenceTransformer

router = APIRouter(prefix="/chat", tags=["chat"])  # ADD prefix + tags for Swagger visibility!

logger = logging.getLogger(__name__)

# Lazy load heavy stuff to avoid startup delay/crash
vector_store = None
embedder = None
groq_client = None

def get_clients():
    global vector_store, embedder, groq_client
    if embedder is None:
        embedder = SentenceTransformer("all-MiniLM-L6-v2")
    if vector_store is None:
        vector_store = VectorStore(collection_name="enterprise_knowledge")
    if groq_client is None:
        if not settings.GROQ_API_KEY:
            raise RuntimeError("GROQ_API_KEY missing")
        groq_client = Groq(api_key=settings.GROQ_API_KEY)
    return vector_store, embedder, groq_client

@router.get("/test")
async def chat_test():
    return {"status": "chat endpoint is live!", "model": "all-MiniLM-L6-v2"}

class ChatRequest(BaseModel):
    query: str

@router.post("/")  # Use "/" with prefix="/chat" → becomes /chat/
async def chat(request: ChatRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    try:
        v_store, emb, g_client = get_clients()
        query_embedding = emb.encode(request.query).tolist()
        search_results = v_store.search(query_embedding, limit=5)
        context = "\n\n".join(result.payload.get("text", "") for result in search_results if result.payload)
        if not context.strip():
            context = "No relevant documents found."
        prompt = f"""You are an expert assistant. Use only this context:
{context}
Question: {request.query}
Answer:"""
        completion = g_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
            temperature=0.3,
        )
        answer = completion.choices[0].message.content.strip()
        return {"answer": answer}
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="AI response failed")