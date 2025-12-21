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
            timeout=60,  # Increase timeout for cloud
        )

        self._init_collection()

    def _init_collection(self):
        try:
            collections = self.client.get_collections()
            collection_names = [c.name for c in collections.collections]

            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=384,
                        distance=Distance.COSINE,
                    ),
                )
        except Exception as e:
            print(f"Collection init error: {e}")

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
        try:
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=limit,
                with_payload=True,
                with_vectors=False,
            )
            return search_result
        except Exception as e:
            print(f"Search error: {e}")
            return []