from fastembed import TextEmbedding
from typing import List
import logging

logger = logging.getLogger(__name__)

class EmbedClient:
    _model = None

    def embed(self, texts: List[str]) -> List[List[float]]:
        if EmbedClient._model is None:
            logger.info("First time: Loading FastEmbed model (this takes 15-30 seconds)...")
            EmbedClient._model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
            logger.info("Model loaded successfully!")

        embeddings = list(EmbedClient._model.embed(texts))
        return [emb.tolist() for emb in embeddings]