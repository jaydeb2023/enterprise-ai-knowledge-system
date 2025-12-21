from fastapi import APIRouter
from pydantic import BaseModel
import logging
from fastapi.concurrency import run_in_threadpool

router = APIRouter()
logger = logging.getLogger(__name__)

class ChatRequest(BaseModel):
    query: str

@router.get("/test")
async def chat_test():
    return {"status": "chat router loaded"}

@router.post("/")
async def chat(req: ChatRequest):
    try:
        from app.clients.embed_client import EmbedClient
        from app.clients.vector_client import VectorStore
        from app.clients.llm_client import LLMClient

        if not req.query or not req.query.strip():
            return {"answer": "Please enter a valid question."}

        # 1️⃣ Embed the question (RUN IN THREADPOOL)
        embed_client = EmbedClient()
        embeddings = await run_in_threadpool(
            embed_client.embed,
            [req.query.strip()]
        )
        query_embedding = embeddings[0]

        # 2️⃣ Vector search (RUN IN THREADPOOL)
        vector_store = VectorStore(collection_name="enterprise_knowledge")
        results = await run_in_threadpool(
            vector_store.search,
            query_embedding,
            5
        )

        logger.info(f"Retrieved {len(results)} chunks for query: '{req.query}'")

        if not results:
            return {
                "answer": "I couldn't find relevant information in the uploaded documents."
            }

        # 3️⃣ Build context
        context = "\n\n".join(
            hit.payload.get("text", "")
            for hit in results
            if isinstance(hit.payload, dict)
        )

        prompt = f"""You are a helpful assistant. Answer the question using ONLY the following context from uploaded documents.
If the context does not contain the answer, say "I don't have that information in the documents."

Context:
{context}

Question: {req.query}

Answer:"""

        # 4️⃣ LLM call (🔥 CRITICAL FIX 🔥)
        llm_client = LLMClient()
        answer = await run_in_threadpool(
            llm_client.generate,
            prompt
        )

        return {"answer": answer.strip() or "No answer generated."}

    except Exception:
        logger.exception("Chat endpoint error")
        return {
            "answer": "Temporary error. Please try again in a few seconds."
        }
