from fastapi import APIRouter
from pydantic import BaseModel
import logging
from fastapi.concurrency import run_in_threadpool

router = APIRouter()
logger = logging.getLogger(__name__)

# 🔥 ADD document_id (ONLY CHANGE IN MODEL)
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

        # 2️⃣ Vector search (🔥 FILTER BY document_id)
        vector_store = VectorStore(collection_name="enterprise_knowledge")
        results = await run_in_threadpool(
            vector_store.search,
            query_embedding,
            10,
            {
                "must": [
                    {
                        "key": "document_id",
                        "match": {"value": req.document_id}
                    }
                ]
            }
        )

        logger.info(
            f"Retrieved {len(results)} chunks "
            f"for query='{req.query}' "
            f"document_id='{req.document_id}'"
        )

        if not results:
            return {
                "answer": "I couldn't find any relevant information in the uploaded document. "
                          "The document may be scanned (image-based) with no extractable text."
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
                "answer": "The uploaded document appears to be scanned (image-based). "
                          "No readable text was found. Try uploading a searchable PDF."
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
            "answer": f"Error processing query: {str(e)}. "
                      "This may be due to a scanned PDF with no extractable text."
        }
