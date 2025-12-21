import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.clients.embed_client import EmbedClient

app = FastAPI(
    title="Enterprise AI Knowledge System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ✅ CORRECT CORS CONFIG (FIXES FAILED TO FETCH)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # Allow all origins (Vercel, localhost, etc.)
    allow_credentials=False,      # ❗ MUST be False with "*"
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
def root():
    return {"message": "Enterprise AI Knowledge System API is running"}

# Health check
@app.get("/health")
def health():
    return {"status": "ok"}

# ✅ Preload embedding model on startup (prevents first-request delay)
@app.on_event("startup")
async def preload_embedding_model():
    print("Pre-loading embedding model on startup...")
    embed_client = EmbedClient()
    embed_client.embed(["warmup text to load model"])
    print("Embedding model pre-loaded successfully!")

# Routers
from app.api.v1.documents import router as documents_router
from app.api.v1.chat import router as chat_router

app.include_router(documents_router, prefix="/documents", tags=["documents"])
app.include_router(chat_router, prefix="/chat", tags=["chat"])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        log_level="info",
        reload=False,
    )
