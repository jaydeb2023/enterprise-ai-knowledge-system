from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import auth, health, documents, chat, admin
from app.db.base import Base
from app.db.session import engine

# Create all database tables (on startup)
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Enterprise AI Knowledge System",
    description="Private RAG System with Qdrant, Groq LLM, Multi-format Document Support",
    version="1.0.0"
)

# === ADD CORS MIDDLEWARE (CRITICAL FIX FOR "Failed to fetch") ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",   # Your Vite/React frontend
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allows GET, POST, PUT, DELETE, etc.
    allow_headers=["*"],  # Allows all headers (Content-Type, Authorization, etc.)
)

# Optional: For production later, you can change allow_origins to your real domain
# Or use allow_origins=["*"] only during development (less secure)

# Include API routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(health.router, prefix="/api/v1")
app.include_router(documents.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")

# Optional: Add a root endpoint for testing
@app.get("/")
async def root():
    return {"message": "Enterprise AI Knowledge System API is running!"}