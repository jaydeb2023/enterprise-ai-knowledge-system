from fastapi import APIRouter
from pydantic import BaseModel
import logging
from fastapi.concurrency import run_in_threadpool

# 🔥 ADD THESE IMPORTS (REQUIRED)
from qdrant_client.models import Filter, FieldCondition, MatchValue

router = APIRouter()
logger = logging.getLogger(__name__)

class ChatRequest(BaseModel):
    query: str
    document_id: str


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

        # 1️⃣ Embed the question
        embed_client = EmbedClient()
        embeddings = await run_in_threadpool(
            embed_client.embed,
            [req.query.strip()]
        )
        query_embedding = embeddings[0]

        # 🔥 BUILD PROPER QDRANT FILTER (THIS IS THE FIX)
        document_filter = Filter(
            must=[
                FieldCondition(
                    key="document_id",
                    match=MatchValue(value=req.document_id)
                )
            ]
        )

        # 2️⃣ Vector search (FILTERED)
        vector_store = VectorStore(collection_name="enterprise_knowledge")
        results = await run_in_threadpool(
            vector_store.search,
            query_embedding,
            10,
            document_filter
        )

        logger.info(
            f"Retrieved {len(results)} chunks "
            f"for query='{req.query}' "
            f"document_id='{req.document_id}'"
        )

        if not results:
            return {
                "answer": "I couldn't find any relevant information in the uploaded document."
            }

        # 3️⃣ Build context (unchanged)
        context_parts = []
        for hit in results:
            if isinstance(hit.payload, dict):
                text = hit.payload.get("text", "").strip()
                if text:
                    context_parts.append(text)

        context = "\n\n".join(context_parts)

        if not context.strip():
            return {
                "answer": "I don't have enough information in the document."
            }

        prompt = f"""You are a helpful assistant. Answer the question using ONLY the following context from uploaded documents.
If the context does not contain enough information, say "I don't have enough information."

Context:
{context}

Question: {req.query}

Answer:"""

        # 4️⃣ LLM call (unchanged)
        llm_client = LLMClient()
        answer = await run_in_threadpool(
            llm_client.generate,
            prompt
        )

        return {"answer": answer.strip() or "No answer generated."}

    except Exception as e:
        logger.exception("Chat endpoint error")
        return {
            "answer": f"Error processing query: {str(e)}"
        }
