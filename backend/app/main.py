import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import auth, health, documents, chat, admin
from app.db.base import Base
from app.db.session import engine

# ===============================
# Database initialization
# ===============================
Base.metadata.create_all(bind=engine)

# ===============================
# Create FastAPI app
# ===============================
app = FastAPI(
    title="Enterprise AI Knowledge System",
    description="Private RAG System with Qdrant, Groq LLM, Multi-format Document Support",
    version="1.0.0"
)

# ===============================
# CORS Middleware
# ===============================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        # Add your Railway frontend domain later if needed
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===============================
# API Routers
# ===============================
app.include_router(auth.router, prefix="/api/v1")
app.include_router(health.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")

# ===============================
# Root endpoint (health check)
# ===============================
@app.get("/")
async def root():
    return {
        "status": "ok",
        "message": "Enterprise AI Knowledge System API is running"
    }

# ===============================
# Railway / Production startup
# ===============================
if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8001))

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
    )
