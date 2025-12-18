from fastapi import APIRouter, Header, Body
from pydantic import BaseModel

from app.services.rag_service import RAGService

router = APIRouter(prefix="/chat", tags=["chat"])

rag = RAGService()


class QueryRequest(BaseModel):
    query: str


@router.post("")
def chat(
    request: QueryRequest,
    x_user_id: str = Header(default="anonymous"),
):
    return rag.answer_question(
        question=request.query,
        user_id=x_user_id,
    )