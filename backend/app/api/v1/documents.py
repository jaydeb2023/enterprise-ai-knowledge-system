from fastapi import APIRouter, UploadFile, Depends, HTTPException, File, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import tempfile
import os
import logging

from app.db.session import SessionLocal
from app.clients.vector_client import VectorStore

import PyPDF2
from docx import Document
from fastapi import Request

# FastEmbed
from fastembed import TextEmbedding

router = APIRouter(tags=["documents"])

vector_store = VectorStore(collection_name="enterprise_knowledge")

# Embedding model singleton
_embedding_model = None

def get_embedding_model():
    global _embedding_model
    if _embedding_model is None:
        print("Loading FastEmbed model...")
        _embedding_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
    return _embedding_model

def embed_texts(texts: list[str]) -> list[list[float]]:
    model = get_embedding_model()
    embeddings = list(model.embed(texts))
    return [embedding.tolist() for embedding in embeddings]

ALLOWED_EXTENSIONS = {
    ".txt", ".md", ".csv",
    ".pdf",
    ".docx", ".doc",
    ".xlsx", ".xls",
    ".pptx", ".ppt",
    ".html", ".htm",
    ".jpg", ".jpeg", ".png", ".tiff"
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def extract_text_safe(file_path: str, filename: str) -> str
    # ... your existing extract_text_safe function (keep as is)
    # (same as before)

# CRITICAL FIX: Explicit OPTIONS for preflight on upload
@router.options("/upload")
async def options_upload():
    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Max-Age": "86400",
        }
    )

@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # ... your existing upload_document code (keep exactly as is)
    # (the long function you had)

@router.get("/test")
async def test_documents():
    return {"documents_service": "ok"}