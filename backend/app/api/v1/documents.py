from fastapi import APIRouter, UploadFile, Depends, HTTPException, File, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import tempfile
import os
import logging
import uuid

from app.db.session import SessionLocal
from app.clients.vector_client import VectorStore
from app.clients.embed_client import EmbedClient  # Same embedder as chat

import PyPDF2
from docx import Document
from bs4 import BeautifulSoup

# ==============================
# ROUTER
# ==============================
router = APIRouter(tags=["documents"])

# ==============================
# VECTOR STORE
# ==============================
vector_store = VectorStore(collection_name="enterprise_knowledge")

# ==============================
# CONFIG
# ==============================
ALLOWED_EXTENSIONS = {
    ".txt", ".md", ".csv",
    ".pdf",
    ".docx",
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
# TEXT EXTRACTION
# ==============================
def extract_text_safe(file_path: str, filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()

    try:
        if ext == ".pdf":
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                return "\n".join(page.extract_text() or "" for page in reader.pages).strip()

        elif ext in [".txt", ".md", ".csv"]:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read().strip()

        elif ext == ".docx":
            doc = Document(file_path)
            return "\n".join(p.text for p in doc.paragraphs if p.text.strip()).strip()

        elif ext in [".html", ".htm"]:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                soup = BeautifulSoup(f.read(), "html.parser")
                return soup.get_text(separator="\n").strip()

        elif ext in [".jpg", ".jpeg", ".png", ".tiff"]:
            return f"[Image file: {filename}]"

        else:
            return ""

    except Exception as e:
        logger.error(f"Text extraction failed: {e}")
        return ""

# ==============================
# OPTIONS (CORS PREFLIGHT)
# ==============================
@router.options("/upload")
async def options_upload():
    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Max-Age": "86400",
        },
    )

# ==============================
# SMART CHUNKING
# ==============================
def smart_chunk_text(text: str) -> list[str]:
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    chunks = []
    current = ""

    for line in lines:
        if len(current) + len(line) <= 300:
            current += line + "\n"
        else:
            chunks.append(current.strip())
            current = line + "\n"

    if current.strip():
        chunks.append(current.strip())

    return list(dict.fromkeys(chunks))

# ==============================
# UPLOAD ENDPOINT
# ==============================
@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
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
        # ✅ Generate document_id PER UPLOAD (FIX)
        document_id = str(uuid.uuid4())

        with tempfile.NamedTemporaryFile(delete=False, suffix=ext, dir="/tmp") as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        text = extract_text_safe(tmp_path, file.filename)
        if not text or len(text) < 10:
            raise HTTPException(status_code=400, detail="No meaningful text extracted from the document")

        chunks = smart_chunk_text(text)

        logger.info(f"Indexing {len(chunks)} chunks")

        embed_client = EmbedClient()
        embeddings = embed_client.embed(chunks)

        payloads = [
            {
                "text": chunk,
                "filename": file.filename,
                "document_id": document_id,   # ✅ ADD ONLY THIS FIELD
                "chunk_index": i,
            }
            for i, chunk in enumerate(chunks)
        ]

        vector_store.add_embeddings(embeddings, payloads)

        return JSONResponse(
            status_code=200,
            content={
                "message": "Document uploaded and indexed successfully",
                "filename": file.filename,
                "document_id": document_id,   # ✅ RETURN IT
                "chunks_stored": len(chunks),
            },
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
