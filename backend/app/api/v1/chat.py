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
        from app.clients.embed_client import EmbedClient
        from app.clients.vector_client import VectorStore
        from app.clients.llm_client import LLMClient

        if not req.query or not req.query.strip():
            return {"answer": "Please enter a valid question."}

        # 1. Embed the question
        embed_client = EmbedClient()
        query_embedding = embed_client.embed([req.query.strip()])[0]

        # 2. Search in Qdrant
        vector_store = VectorStore(collection_name="documents")
        results = vector_store.search(query_embedding, limit=5)

        logger.info(f"Retrieved {len(results)} chunks for query: '{req.query}'")

        # 3. No relevant chunks found
        if not results or len(results) == 0:
            return {
                "answer": "I couldn't find relevant information in the uploaded documents. "
                          "Please make sure a document is uploaded and try a more specific question."
            }

        # 4. Build context from retrieved chunks
        context = "\n\n".join([
            hit.payload.get("text", "") if isinstance(hit.payload, dict) else ""
            for hit in results
        ])

        # 5. Strict RAG prompt
        prompt = f"""You are a helpful assistant. Answer the question using ONLY the following context from uploaded documents.
If the context does not contain the answer, say "I don't have that information in the documents."

Context:
{context}

Question: {req.query}

Answer:"""

        # 6. Generate with Groq
        llm_client = LLMClient()
        answer = llm_client.generate(prompt)

        return {"answer": answer.strip() or "No answer generated."}

    except Exception as e:
        logger.exception("Chat endpoint error")
        return {
            "answer": "Temporary error. Please try again in a few seconds."
        }