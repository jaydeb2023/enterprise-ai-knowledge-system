from fastapi import APIRouter
from app.clients.vector_client import VectorStore

router = APIRouter(prefix="/admin/vectors", tags=["Admin Vectors"])

@router.get("/collections")
def list_collections():
    vs = VectorStore(collection_name="enterprise_docs")
    return vs.client.get_collections()

@router.get("/points")
def list_vectors(limit: int = 5):
    vs = VectorStore(collection_name="enterprise_docs")
    points, _ = vs.client.scroll(
        collection_name="enterprise_docs",
        limit=limit
    )
    return {
        "count": len(points),
        "points": points
    }
