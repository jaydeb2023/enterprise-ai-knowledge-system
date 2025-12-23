import os
import uuid
from typing import List, Optional

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    PayloadSchemaType,   # 🔥 ADD
)

class VectorStore:
    def __init__(self, collection_name: str = "documents"):
        self.collection_name = collection_name

        self.client = QdrantClient(
            url=os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API_KEY"),
            timeout=60,
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

            # 🔥 ADD PAYLOAD INDEX FOR document_id (CRITICAL FIX)
            try:
                self.client.create_payload_index(
                    collection_name=self.collection_name,
                    field_name="document_id",
                    field_schema=PayloadSchemaType.KEYWORD,
                )
            except Exception as e:
                # Index may already exist — safe to ignore
                print(f"Payload index creation skipped: {e}")

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

    def search(
        self,
        query_vector: List[float],
        limit: int = 5,
        query_filter: Optional[Filter] = None,
    ):
        try:
            search_result = self.client.query_points(
                collection_name=self.collection_name,
                query=query_vector,
                limit=limit,
                with_payload=True,
                query_filter=query_filter,
            )
            return search_result.points
        except Exception as e:
            print(f"Search error: {e}")
            return []
