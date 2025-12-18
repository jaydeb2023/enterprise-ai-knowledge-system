from app.services.embedding_service import EmbeddingService
from app.clients.vector_client import VectorStore
from app.clients.llm_client import LLMClient
from app.services.cache_service import CacheService
from app.core.rate_limit import RATE_LIMIT_REQUESTS, RATE_LIMIT_WINDOW


class RAGService:
    def __init__(self):
        self.embedder = EmbeddingService()
        self.vector_store = VectorStore(collection_name="enterprise_docs")
        self.llm = LLMClient()
        self.cache = CacheService()

    def answer_question(self, question: str, user_id: str = "anonymous") -> dict:
        # ---------- RATE LIMIT ----------
        rate_key = f"rate:{user_id}"
        if self.cache.is_rate_limited(
            rate_key,
            RATE_LIMIT_REQUESTS,
            RATE_LIMIT_WINDOW,
        ):
            return {
                "error": "Rate limit exceeded. Please try again later."
            }

        # ---------- CACHE ----------
        cache_key = f"rag:{question}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        # ---------- EMBED QUERY ----------
        query_vector = self.embedder.embed_query(question)

        # ---------- VECTOR SEARCH ----------
        results = self.vector_store.search(
            query_vector=query_vector,
            limit=5,
        )

        if not results:
            response = {
                "answer": "I could not find relevant information.",
                "sources": [],
            }
            self.cache.set(cache_key, response)
            return response

        # ---------- CONTEXT BUILD ----------
        context_chunks = []
        sources = []

        for hit in results:
            payload = hit.payload
            context_chunks.append(payload["text"])
            sources.append(
                {
                    "document_id": payload["document_id"],
                    "filename": payload["filename"],
                }
            )

        context = "\n\n".join(context_chunks)

        prompt = f"""
Use the following context to answer the question.

Context:
{context}

Question:
{question}
"""

        # ---------- LLM CALL ----------
        answer = self.llm.generate(prompt)

        response = {
            "answer": answer,
            "sources": sources,
        }

        # ---------- CACHE RESPONSE ----------
        self.cache.set(cache_key, response)

        return response
