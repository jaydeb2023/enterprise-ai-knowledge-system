from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Enterprise AI Knowledge System",
    version="1.0.0"
)

# CORS (safe default)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "ok", "service": "enterprise-ai-knowledge-system"}

@app.get("/health")
def health():
    return {"health": "healthy"}
