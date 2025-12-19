from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)

class ChatRequest(BaseModel):
    query: str

@router.get("/test")
async def test():
    return {"chat": "ok"}

@router.post("")
async def chat(req: ChatRequest):
    return {"answer": "chat route is alive"}
