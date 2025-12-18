from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from typing import List
import uuid


class VectorStore:
    def __init__(self, collection_name: str):
        self.client = QdrantClient(host="localhost", port=6333)
        self.collection_name = collection_name
        self._init_collection()

    def _init_collection(self):
        collections = self.client.get_collections().collections
        if self.collection_name not in [c.name for c in collections]:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=384,  # sentence-transformers dimension
                    distance=Distance.COSINE,
                ),
            )

    def add_embeddings(self, embeddings: List[List[float]], payloads: List[dict]):
        points = []
        for emb, payload in zip(embeddings, payloads):
            points.append(
                PointStruct(
                    id=str(uuid.uuid4()),
                    vector=emb,
                    payload=payload,
                )
            )

        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
        )

    def search(self, query_vector: List[float], limit: int = 5):
        return self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit,
        )
