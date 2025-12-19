from fastapi import FastAPI

app = FastAPI(
    title="Enterprise AI Knowledge System",
    version="1.0.0"
)

@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/health")
def health():
    return {"health": "healthy"}

@app.post("/embed")
def embed(text: str):
    return {
        "error": "ML disabled on Railway free tier",
        "message": "Deploy ML as a separate service"
    }
