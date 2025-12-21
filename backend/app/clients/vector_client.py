import os
import uuid
from typing import List

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

class VectorStore:
    def __init__(self, collection_name: str = "documents"):
        self.collection_name = collection_name

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
                    size=384,
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
        # This is the correct, stable method in current qdrant-client
        hits = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit,
            with_payload=True,  # Get the text
            with_vectors=False,
        )
        return hits