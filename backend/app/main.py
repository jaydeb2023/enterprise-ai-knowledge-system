from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Enterprise AI Knowledge System",
    version="1.0.0",
    description="Backend API for chat and document management with enterprise knowledge",
    docs_url="/docs",      # Swagger UI
    redoc_url="/redoc",    # Alternative docs
)

# -------------------------
# CORS - Critical for React frontend
# -------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # In production, replace with your React domain, e.g. ["https://your-frontend.up.railway.app"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# Simple root for health/debug
# -------------------------
@app.get("/")
def root():
    return {"status": "running", "message": "Enterprise AI Backend is live!"}

# -------------------------
# Health check - Fast & reliable
# -------------------------
@app.get("/health")
def health():
    return {"status": "ok"}

# -------------------------
# Include your API routers
# -------------------------
from app.api.v1.health import router as health_router
from app.api.v1.documents import router as documents_router
from app.api.v1.chat import router as chat_router

app.include_router(health_router)                    # /health (backup if needed)
app.include_router(documents_router, prefix="/documents")
app.include_router(chat_router, prefix="/chat")       # /chat and /chat/test