from fastapi import APIRouter, UploadFile, Depends, HTTPException, File, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import tempfile
import os
import logging

from app.db.session import SessionLocal
from app.services.ingest_service import ingest_document

router = APIRouter(prefix="/documents", tags=["documents"])

# Supported extensions (you can add more later)
ALLOWED_EXTENSIONS = {
    ".txt", ".md", ".csv",
    ".pdf",
    ".docx", ".doc",
    ".xlsx", ".xls",
    ".pptx", ".ppt",
    ".html", ".htm",
    ".jpg", ".jpeg", ".png", ".tiff"  # Images with OCR
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
    """
    Use unstructured to extract clean text from any supported document type.
    Returns plain text string.
    """
    try:
        from unstructured.partition.auto import partition

        elements = partition(filename=file_path, strategy="auto")
        
        # Join all text elements, preserve paragraphs
        text_parts = []
        for element in elements:
            if element.text:
                text_parts.append(element.text.strip())
        
        full_text = "\n\n".join([part for part in text_parts if part])
        return full_text

    except Exception as e:
        logger.error(f"Error extracting text from {filename}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")


@router.post("/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Validate file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file_ext} not supported. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Security: prevent very large files (adjust as needed)
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 50MB)")

    # Save to temp file for unstructured processing
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp_file:
            tmp_file.write(content)
            tmp_path = tmp_file.name

        logger.info(f"Extracting text from uploaded file: {file.filename}")
        text = extract_text_with_unstructured(tmp_path, file.filename)

        if not text.strip():
            raise HTTPException(status_code=400, detail="No text could be extracted from the file")

        # Ingest into vector DB (Qdrant via your service)
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
        logger.error(f"Unexpected error during upload: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during processing")
    finally:
        # Clean up temp file
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except:
                pass