from fastembed import TextEmbedding
from typing import List
import logging

logger = logging.getLogger(__name__)

class EmbedClient:
    _model = None

    def embed(self, texts: List[str]) -> List[List[float]]:
        if EmbedClient._model is None:
            logger.info("Loading lightweight embedding model (fast first time)...")
            # ← CHANGE THIS LINE ONLY
            EmbedClient._model = TextEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")
            logger.info("Model loaded!")
        embeddings = list(EmbedClient._model.embed(texts))
        return [emb.tolist() for emb in embeddings]