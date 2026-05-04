import numpy as np
from rag.embeddings import EmbeddingModel
from core.vector_db import VectorDatabase

class Retriever:
    def __init__(self, embedding_model: EmbeddingModel, vector_db: VectorDatabase):
        self.embedding_model = embedding_model
        self.vector_db = vector_db

    def retrieve(self, query: str, k: int = 3) -> list[dict]:
        """Retrieve relevant documents for a query."""
        query_embedding = self.embedding_model.encode_single(query)
        results = self.vector_db.search(query_embedding, k)
        return [result[2] for result in results]  # Return metadata