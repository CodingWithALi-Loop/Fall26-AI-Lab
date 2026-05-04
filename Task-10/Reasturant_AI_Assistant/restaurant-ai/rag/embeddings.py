import numpy as np

class EmbeddingModel:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model_name = model_name
        self.model = None

    def _load_model(self):
        if self.model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer(self.model_name)
            except Exception as e:
                raise RuntimeError(f"Failed to load embedding model: {e}")

    def encode(self, texts: list[str]) -> np.ndarray:
        """Encode a list of texts into embeddings."""
        self._load_model()
        return self.model.encode(texts, convert_to_numpy=True)

    def encode_single(self, text: str) -> np.ndarray:
        """Encode a single text into an embedding."""
        self._load_model()
        return self.model.encode([text], convert_to_numpy=True)[0]