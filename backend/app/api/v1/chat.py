from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.clients.vector_client import VectorStore
from app.core.config import settings
from groq import Groq
import logging

from sentence_transformers import SentenceTransformer

# === CREATE ROUTER FIRST ===
router = APIRouter(tags=["chat"])

logger = logging.getLogger(__name__)

# Initialize clients
vector_store = VectorStore(collection_name="enterprise_knowledge")
embedder = SentenceTransformer("all-MiniLM-L6-v2")
groq_client = Groq(api_key=settings.GROQ_API_KEY)

# === TEST ENDPOINT (now router exists) ===
@router.get("/test")
async def chat_test():
    return {"status": "chat endpoint is live!", "model": "all-MiniLM-L6-v2"}

# === REQUEST MODEL ===
class ChatRequest(BaseModel):
    query: str

# === MAIN CHAT ENDPOINT ===
@router.post("/chat")
async def chat(request: ChatRequest):
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    try:
        # Generate query embedding
        query_embedding = embedder.encode(request.query).tolist()

        # Search in Qdrant
        search_results = vector_store.search(query_embedding, limit=5)

        context = ""
        for result in search_results:
            payload = result.payload or {}
            text = payload.get("text", "")
            if text:
                context += text + "\n\n"

        if not context.strip():
            context = "No relevant documents found in the uploaded documents."

        # Prompt for Groq
        prompt = f"""You are an expert assistant for Enterprise Knowledge.

Use only the following context to answer the question. If the answer is not in the context, say "I don't have information about that in the uploaded documents."

Context:
{context}

Question: {request.query}

Answer:"""

        chat_completion = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
            temperature=0.3,
        )

        answer = chat_completion.choices[0].message.content.strip()

        return {"answer": answer}

    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate AI response")