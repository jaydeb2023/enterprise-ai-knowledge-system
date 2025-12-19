from fastapi import APIRouter, UploadFile, Depends, HTTPException, File, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import tempfile
import os
import logging

from app.db.session import SessionLocal
from app.clients.vector_client import VectorStore
from app.core.config import settings
from groq import Groq

import PyPDF2
from docx import Document

# ==============================
# ROUTER
# ==============================
router = APIRouter(tags=["documents"])

# ==============================
# CLIENTS (SAFE)
# ==============================
vector_store = VectorStore(collection_name="enterprise_knowledge")

_groq_client = None

def get_groq_client():
    global _groq_client
    if _groq_client is None:
        if not settings.GROQ_API_KEY:
            raise RuntimeError("GROQ_API_KEY is not set")
        _groq_client = Groq(api_key=settings.GROQ_API_KEY)
    return _groq_client

def embed_texts(texts: list[str]) -> list[list[float]]:
    client = get_groq_client()
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts
    )
    return [e.embedding for e in response.data]

# ==============================
# CONFIG
# ==============================
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

# ==============================
# DB DEPENDENCY
# ==============================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==============================
# SAFE TEXT EXTRACTION
# ==============================
def extract_text_safe(file_path: str, filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()

    try:
        if ext == ".pdf":
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                return "\n\n".join(page.extract_text() or "" for page in reader.pages).strip()

        elif ext in [".txt", ".md", ".csv"]:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read().strip()

        elif ext == ".docx":
            doc = Document(file_path)
            return "\n\n".join(p.text for p in doc.paragraphs if p.text.strip()).strip()

        elif ext in [".html", ".htm"]:
            from bs4 import BeautifulSoup
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                soup = BeautifulSoup(f.read(), "html.parser")
                return soup.get_text(separator="\n\n").strip()

        elif ext in [".jpg", ".jpeg", ".png", ".tiff"]:
            return f"[Image file: {filename}]"

        else:
            return f"[Unsupported file type: {ext}]"

    except Exception as e:
        logger.error(f"Extraction failed for {filename}: {e}")
        return ""

# ==============================
# OPTIONS
# ==============================
@router.options("/upload")
async def upload_options():
    return {}

# ==============================
# UPLOAD ENDPOINT
# ==============================
@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")

    content = await file.read()
    if len(content) > 50 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large")

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext, dir="/tmp") as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        text = extract_text_safe(tmp_path, file.filename)
        if not text or len(text) < 10:
            raise HTTPException(status_code=400, detail="No meaningful text extracted")

        chunk_size = 500
        chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

        embeddings = embed_texts(chunks)

        payloads = [
            {"text": chunk, "filename": file.filename, "chunk_index": i}
            for i, chunk in enumerate(chunks)
        ]

        vector_store.add_embeddings(embeddings, payloads)

        return JSONResponse(
            status_code=200,
            content={
                "message": "Document uploaded and indexed successfully",
                "filename": file.filename,
                "chunks_stored": len(chunks)
            }
        )

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)

# ==============================
# TEST ENDPOINT
# ==============================
@router.get("/test")
async def test_documents():
    return {"documents_service": "ok"}
