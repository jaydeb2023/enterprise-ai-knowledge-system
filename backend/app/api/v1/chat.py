from fastapi import APIRouter
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
        # Lazy imports to keep startup fast (important for Railway health check)
        from app.clients.embed_client import EmbedClient
        from app.clients.vector_client import VectorStore
        from app.clients.llm_client import LLMClient

        # 1. Embed the user's question
        # Model loads only on first request (10-20s delay once, then instant)
        embed_client = EmbedClient()
        query_embedding = embed_client.embed([req.query])[0]

        # 2. Search in Qdrant
        vector_store = VectorStore(collection_name="documents")
        results = vector_store.search(query_embedding, limit=5)

        logger.info(f"Retrieved {len(results)} relevant document chunks for query: '{req.query}'")

        # 3. No results → friendly message
        if not results:
            return {
                "answer": "I couldn't find any relevant information in the uploaded documents. "
                          "Please make sure you have uploaded and indexed files first."
            }

        # 4. Extract text from payloads
        context_parts = []
        for point in results:
            payload = point.payload
            text = payload.get("text", "") if isinstance(payload, dict) else ""
            context_parts.append(text)

        context = "\n\n".join(context_parts)

        # 5. Create strict RAG prompt
        prompt = f"""You are a helpful assistant that answers questions using ONLY the provided context from uploaded documents.

Context:
{context}

Question: {req.query}

Answer (be concise and accurate):"""

        # 6. Call Groq LLM
        llm_client = LLMClient()
        answer = llm_client.generate(prompt)

        return {"answer": answer.strip()}

    except MemoryError:
        return {
            "answer": "The AI model is warming up (first-time loading). "
                      "Please try your question again in 20-30 seconds."
        }
    except Exception as e:
        logger.exception("Unexpected error in chat endpoint")
        # Return friendly message instead of 500 error
        return {
            "answer": "Sorry, something went wrong. Please try again in a moment."
        }