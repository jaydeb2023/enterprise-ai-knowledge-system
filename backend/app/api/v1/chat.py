from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging
from typing import List

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
        from app.clients.llm_client import LLMClient
        from app.clients.embed_client import EmbedClient
        from app.core.config import settings

        if not settings.GROQ_API_KEY:
            raise RuntimeError("GROQ_API_KEY missing")

        # 1. Embed query
        embed_client = EmbedClient()
        query_embedding = embed_client.embed([req.query])[0]  # Returns list of lists → take first

        # 2. Retrieve from Qdrant
        vector_store = VectorStore(collection_name="documents")
        results = vector_store.search(query_embedding, limit=5)

        logger.info(f"Retrieved {len(results)} chunks for query: '{req.query}'")

        # 3. Build context
        if not results:
            return {"answer": "No relevant information found in the uploaded documents. Please upload documents first."}

        context = "\n\n".join([
            r.payload.get("text", "") if isinstance(r.payload, dict) else ""
            for r in results
        ])

        # 4. RAG Prompt
        prompt = f"""You are a helpful assistant. Answer the user's question using ONLY the following context from uploaded documents.
If the context does not contain enough information, say "I couldn't find that information in the documents."

Context:
{context}

Question: {req.query}

Answer:"""

        # 5. Generate with Groq
        llm_client = LLMClient()
        answer = llm_client.generate(prompt)

        return {"answer": answer}

    except Exception as e:
        logger.exception("Chat error")
        raise HTTPException(status_code=500, detail=str(e))