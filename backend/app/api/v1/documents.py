from fastapi import APIRouter, UploadFile, Depends, HTTPException, File, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import tempfile
import os
import logging

from app.db.session import SessionLocal
from app.services.ingest_service import ingest_document

# IMPORTANT:
# ❌ NO prefix here
# ✅ Prefix is applied in main.py
router = APIRouter(tags=["documents"])

# Supported extensions
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


def extract_text_with_unstructured(file_path: str, filename: str) -> str:
    try:
        from unstructured.partition.auto import partition

        elements = partition(filename=file_path, strategy="auto")

        text_parts = []
        for element in elements:
            if element.text:
                text_parts.append(element.text.strip())

        return "\n\n".join([p for p in text_parts if p])

    except Exception as e:
        logger.error(f"Error extracting text from {filename}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process file")


# =====================================================
# ✅ REQUIRED FOR MOBILE BROWSERS (VERY IMPORTANT)
# =====================================================
@router.options("/upload")
async def upload_options():
    return {}


# =====================================================
# ✅ UPLOAD ENDPOINT
# URL WILL BE: /documents/upload
# =====================================================
@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file_ext} not supported"
        )

    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large")

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            tmp_file.write(content)
            tmp_path = tmp_file.name

        logger.info(f"Processing file: {file.filename}")
        text = extract_text_with_unstructured(tmp_path, file.filename)

        if not text.strip():
            raise HTTPException(status_code=400, detail="No text extracted")

        result = ingest_document(
            db=db,
            filename=file.filename,
            content=text
        )

        return JSONResponse({
            "message": "Document uploaded and indexed successfully",
            "filename": file.filename,
            "document_id": result.get("document_id"),
            "chunks_indexed": result.get("chunks_indexed"),
            "extracted_text_length": len(text)
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except:
                pass
