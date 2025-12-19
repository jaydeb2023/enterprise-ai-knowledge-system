from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# Add this with other imports
from app.api.v1.chat import router as chat_router

# Add this with other include_router calls
app.include_router(chat_router)
# =========================
# APP
# =========================
app = FastAPI(
    title="Enterprise AI Knowledge System",
    version="1.0.0"
)

# =========================
# CORS (PUBLIC / MOBILE SAFE)
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# ROOT
# =========================
@app.get("/")
async def root():
    return {"status": "ok"}

# =========================
# IMPORT ROUTERS
# =========================
from app.api.v1.health import router as health_router
from app.api.v1.documents import router as documents_router

# =========================
# INCLUDE ROUTERS
# =========================
app.include_router(health_router)
app.include_router(documents_router, prefix="/documents")
