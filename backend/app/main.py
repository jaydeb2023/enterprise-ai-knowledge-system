from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Enterprise AI Knowledge System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔴 HEALTHCHECK — DIRECT (NO ROUTERS)
@app.get("/health")
def health():
    return {"status": "ok"}

# ROOT
@app.get("/")
def root():
    return {"status": "running"}
