from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Enterprise AI Knowledge System",
    description="AI-powered chat with enterprise documents",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS for React frontend (Vercel or local)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to your Vercel URL later for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint
@app.get("/")
def root():
    return {"status": "running", "message": "Enterprise AI Backend is live!"}

# Fast health check (Railway loves this)
@app.get("/health")
def health():
    return {"status": "ok"}

# Include routers
from app.api.v1.health import router as health_router
from app.api.v1.documents import router as documents_router
from app.api.v1.chat import router as chat_router

app.include_router(health_router)
app.include_router(documents_router, prefix="/documents", tags=["documents"])
app.include_router(chat_router, prefix="/chat", tags=["chat"])