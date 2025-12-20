from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging
from typing import List
import numpy as np  # for FastEmbed

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
        from app.clients.embed_client import EmbedClient  # You'll need this (see below)
        from app.core.config import settings

        if not settings.GROQ_API_KEY:
            raise RuntimeError("GROQ_API_KEY missing")

        # 1. Embed query
        embed_client = EmbedClient()  # Assuming you have this client
        query_embedding = embed_client.embed([req.query])[0]  # single query

        # 2. Retrieve from Qdrant
        vector_store = VectorStore(collection_name="documents")  # your collection name
        results = vector_store.search(query_embedding, limit=5)
        
        logger.info(f"Retrieved {len(results)} chunks for query: {req.query}")

        # 3. Build context from payloads
        context = ""
        if results:
            context = "\n\n".join([r.payload.get("text", "No text") for r in results])
        else:
            return {"answer": "No documents found. Please upload documents first."}

        # 4. RAG Prompt for Groq
        prompt = f"""You are a helpful assistant. Answer the question based ONLY on the following context from uploaded documents.
If the context doesn't contain the answer, say "I couldn't find that information in the documents."

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