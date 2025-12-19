from fastapi import APIRouter, UploadFile, Depends, HTTPException, File, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import tempfile
import os
import logging

from app.db.session import SessionLocal

# ==============================
# ROUTER (NO PREFIX HERE)
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
# TEXT EXTRACTION (SAFE)
# ==============================
def extract_text_with_unstructured(file_path: str, filename: str) -> str:
    try:
        from unstructured.partition.auto import partition

        elements = partition(filename=file_path, strategy="auto")

        texts = []
        for el in elements:
            if el.text:
                texts.append(el.text.strip())

        return "\n\n".join(texts)

    except Exception as e:
        logger.error(f"Extraction failed for {filename}: {e}")
        raise HTTPException(status_code=500, detail="Text extraction failed")

# ==============================
# REQUIRED FOR MOBILE (OPTIONS)
# ==============================
@router.options("/upload")
async def upload_options():
    return {}

# ==============================
# UPLOAD ENDPOINT
# URL: /documents/upload
# ==============================
@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Validate extension
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file type")

    # Read file
    content = await file.read()
    if len(content) > 50 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 50MB)")

    tmp_path = None
    try:
        # Save temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        text = extract_text_with_unstructured(tmp_path, file.filename)

        if not text.strip():
            raise HTTPException(status_code=400, detail="No text extracted")

        # 🚨 TEMPORARY RESPONSE (NO INGEST)
        return JSONResponse({
            "message": "Upload OK (public test mode)",
            "filename": file.filename,
            "text_length": len(text)
        })

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail="Upload failed")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except:
                pass
