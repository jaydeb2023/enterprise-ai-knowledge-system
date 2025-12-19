# C:\Users\debja\Downloads\enterprise-ai-knowledge-system\backend\app\api\v1\documents.py
# FULL WORKING VERSION WITH QDRANT STORAGE + EMBEDDINGS

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

# NEW: For embeddings and Qdrant
from sentence_transformers import SentenceTransformer

# Initialize once at startup (efficient)
embedder = SentenceTransformer("all-MiniLM-L6-v2")
vector_store = VectorStore(collection_name="enterprise_knowledge")

# ==============================
# ROUTER
# ==============================
router = APIRouter(tags=["documents"])

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
                text = "\n\n".join(page.extract_text() or "" for page in reader.pages)
                return text.strip()
        
        elif ext in [".txt", ".md", ".csv"]:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read().strip()
        
        elif ext == ".docx":
            doc = Document(file_path)
            return "\n\n".join(para.text for para in doc.paragraphs if para.text.strip()).strip()
        
        elif ext in [".html", ".htm"]:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(f.read(), 'html.parser')
                return soup.get_text(separator="\n\n").strip()
        
        elif ext in [".jpg", ".jpeg", ".png", ".tiff"]:
            return f"[Image file: {filename}] - Text extraction from images not supported yet"
        
        else:
            return f"[Unsupported file type: {ext}]"
    
    except Exception as e:
        logger.error(f"Extraction failed for {filename}: {e}")
        return f"Extraction error: {str(e)}"

# ==============================
# OPTIONS FOR MOBILE
# ==============================
@router.options("/upload")
async def upload_options():
    return {}

# ==============================
# UPLOAD ENDPOINT - NOW STORES IN QDRANT
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
        raise HTTPException(status_code=400, detail="File too large (max 50MB)")

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext, dir="/tmp") as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        text = extract_text_safe(tmp_path, file.filename)
        
        if not text or len(text.strip()) < 10:
            raise HTTPException(status_code=400, detail="No meaningful text extracted")

        # === REAL INDEXING: Split → Embed → Store in Qdrant ===
        chunk_size = 500
        chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

        embeddings = embedder.encode(chunks).tolist()

        payloads = [
            {
                "text": chunk,
                "filename": file.filename,
                "chunk_index": idx
            }
            for idx, chunk in enumerate(chunks)
        ]

        vector_store.add_embeddings(embeddings, payloads)

        # === SUCCESS RESPONSE ===
        return JSONResponse(
            status_code=200,
            content={
                "message": "✅ Document uploaded and indexed successfully!",
                "filename": file.filename,
                "chunks_stored": len(chunks),
                "text_length": len(text),
                "preview": text[:500] + ("..." if len(text) > 500 else "")
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except Exception as e:
                logger.warning(f"Failed to delete temp file: {e}")

# ==============================
# TEST ENDPOINT
# ==============================
@router.get("/test")
async def test_documents():
    return {"documents_service": "ok", "supported_formats": list(ALLOWED_EXTENSIONS)}