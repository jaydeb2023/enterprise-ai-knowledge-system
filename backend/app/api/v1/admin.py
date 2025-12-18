from fastapi import APIRouter
from app.db.session import SessionLocal
from app.models.user import User
from app.clients.vector_client import VectorStore

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/users")
def list_users():
    db = SessionLocal()
    users = db.query(User).all()
    return users

@router.delete("/vectors/reset")
def reset_vectors():
    vs = VectorStore("enterprise_docs")
    vs.client.delete_collection("enterprise_docs")
    return {"status": "Vector DB cleared"}

@router.get("/stats")
def system_stats():
    vs = VectorStore("enterprise_docs")
    collections = vs.client.get_collections()
    return {
        "collections": collections,
        "status": "system healthy"
    }
