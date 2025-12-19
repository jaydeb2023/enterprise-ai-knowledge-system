from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/chat", tags=["chat"])  # prefix + tags = shows nicely in Swagger

class ChatRequest(BaseModel):
    query: str

@router.get("/test")
async def test():
    return {"chat": "ok"}

@router.post("/")
async def chat(req: ChatRequest):
    # Your full AI chat logic here
    return {"answer": "Full response based on documents"}