from fastembed import TextEmbedding
import numpy as np
from typing import List

class EmbedClient:
    def __init__(self):
        # FastEmbed model (matches your 384 dim Qdrant collection)
        self.model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")

    def embed(self, texts: List[str]) -> List[List[float]]:
        embeddings = self.model.embed(texts)
        return [emb.tolist() for emb in embeddings]  # Convert to list for Qdrant