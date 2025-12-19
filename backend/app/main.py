from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# =========================
# APP - CREATE FIRST
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
# IMPORT ROUTERS (AFTER app is created)
# =========================
from app.api.v1.health import router as health_router
from app.api.v1.documents import router as documents_router
from app.api.v1.chat import router as chat_router   # ← Now safe to import

# =========================
# INCLUDE ROUTERS (AFTER imports)
# =========================
app.include_router(health_router)
app.include_router(documents_router, prefix="/documents")
app.include_router(chat_router)   # ← This makes /chat work!