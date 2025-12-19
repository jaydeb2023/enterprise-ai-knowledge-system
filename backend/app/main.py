from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Enterprise AI Knowledge System",
    version="1.0.0"
)

# ✅ CORS (VERY IMPORTANT for Vercel → Railway)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # OK for demo / free tier
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ ROOT (optional)
@app.get("/")
def root():
    return {"status": "ok", "service": "enterprise-ai-knowledge-system"}

# ✅ HEALTH CHECK (THIS WAS MISSING)
@app.get("/api/v1/health")
def health():
    return {"status": "ok", "service": "enterprise-ai-knowledge-system"}

# 🔽 include your routers here
# from app.api.v1.documents import router as documents_router
# app.include_router(documents_router, prefix="/api/v1/documents", tags=["documents"])
