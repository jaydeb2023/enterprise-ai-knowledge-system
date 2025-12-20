from fastembed import TextEmbedding
from typing import List
import logging

logger = logging.getLogger(__name__)

class EmbedClient:
    _model = None
    _lock = False  # Simple lock to prevent double loading

    def __init__(self):
        pass  # No load here

    def _load_model(self):
        if EmbedClient._model is None and not EmbedClient._lock:
            EmbedClient._lock = True
            logger.info("Loading FastEmbed model for the first time... (this may take 10-20 seconds)")
            try:
                EmbedClient._model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
                logger.info("FastEmbed model loaded successfully!")
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
                raise e
            finally:
                EmbedClient._lock = False

    def embed(self, texts: List[str]) -> List[List[float]]:
        self._load_model()
        embeddings = list(EmbedClient._model.embed(texts))
        return [emb.tolist() for emb in embeddings]