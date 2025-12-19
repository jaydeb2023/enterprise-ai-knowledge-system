from fastapi import FastAPI
from typing import Optional
import os

app = FastAPI(
    title="Enterprise AI Knowledge System",
    version="1.0.0",
)

# -------------------------
# Health & Root Endpoints
# -------------------------

@app.get("/")
def root():
    return {"status": "ok", "service": "enterprise-ai-knowledge-system"}

@app.get("/health")
def health():
    return {"health": "healthy"}


# -------------------------
# Lazy-loaded ML model
# -------------------------

_model = None

def get_model():
    """
    Load sentence-transformer model only when needed.
    This prevents Railway from crashing during startup/build.
    """
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


# -------------------------
# Example embedding endpoint
# -------------------------

@app.post("/embed")
def embed(text: str):
    model = get_model()
    embedding = model.encode(text).tolist()
    return {"embedding": embedding}


# -------------------------
# Startup & Shutdown hooks
# -------------------------

@app.on_event("startup")
def on_startup():
    # Do NOT load ML models here
    # Keep startup lightweight for Railway
    pass


@app.on_event("shutdown")
def on_shutdown():
    global _model
    _model = None
