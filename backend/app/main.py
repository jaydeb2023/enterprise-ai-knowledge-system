from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI app
app = FastAPI(
    title="Enterprise AI Knowledge System",
    version="1.0.0"
)

# =====================================================
# CORS CONFIG (PUBLIC / MOBILE SAFE)
# =====================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # allow everyone (public demo)
    allow_credentials=False,    # MUST be False when using "*"
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# ROOT ROUTE
# =====================================================
@app.get("/")
async def root():
    return {
        "status": "ok",
        "service": "enterprise-ai-knowledge-system"
    }

# =====================================================
# HEALTH CHECK (OPTIONAL BUT GOOD)
# =====================================================
@app.get("/health")
async def health():
    return {
        "status": "ok"
    }

# =====================================================
# DOCUMENT ROUTES (UPLOAD / INDEX)
# =====================================================
from app.api.v1.documents import router as documents_router

# IMPORTANT:
# Frontend calls: /documents/upload
# So prefix MUST be "/documents"
app.include_router(
    documents_router,
    prefix="/documents",
    tags=["documents"]
)
