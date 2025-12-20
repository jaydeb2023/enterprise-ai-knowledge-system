import os
import uuid
from typing import List

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from qdrant_client.models import QueryPoints  # New import for modern search


class VectorStore:
    def __init__(self, collection_name: str = "documents"):
        self.collection_name = collection_name

        # ✅ CONNECT TO QDRANT CLOUD
        self.client = QdrantClient(
            url=os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API_KEY"),
        )

        self._init_collection()

    def _init_collection(self):
        collections = self.client.get_collections().collections
        collection_names = [c.name for c in collections]

        if self.collection_name not in collection_names:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=384,  # matches FastEmbed BAAI/bge-small-en-v1.5
                    distance=Distance.COSINE,
                ),
            )

    def add_embeddings(self, embeddings: List[List[float]], payloads: List[dict]):
        points = [
            PointStruct(
                id=str(uuid.uuid4()),
                vector=emb,
                payload=payload,
            )
            for emb, payload in zip(embeddings, payloads)
        ]

        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
        )

    def search(self, query_vector: List[float], limit: int = 5):
        """Modern search using query_points (replaces deprecated .search)"""
        result = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=limit,
            with_payload=True,   # Crucial: get the text back
            with_vectors=False,
        )
        return result.points  # List of ScoredPoint objects