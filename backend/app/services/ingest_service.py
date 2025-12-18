from typing import List
from sqlalchemy.orm import Session

from app.models.document import Document
from app.services.embedding_service import EmbeddingService
from app.clients.vector_client import VectorStore


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap

    return chunks


def ingest_document(
    db: Session,
    filename: str,
    content: str,
):
    document = Document(
        filename=filename,
        content=content,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    chunks = chunk_text(content)

    embedder = EmbeddingService()
    vectors = embedder.embed_texts(chunks)

    vector_store = VectorStore(collection_name="enterprise_docs")

    payloads = [
        {
            "document_id": document.id,
            "text": chunk,
            "filename": filename,
        }
        for chunk in chunks
    ]

    vector_store.add_embeddings(vectors, payloads)

    return {
        "document_id": document.id,
        "chunks_indexed": len(chunks),
    }
