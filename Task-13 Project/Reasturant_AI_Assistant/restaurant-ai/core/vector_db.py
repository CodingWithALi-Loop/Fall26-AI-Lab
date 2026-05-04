import faiss
import numpy as np
import pickle
import os
from pathlib import Path

class VectorDatabase:
    def __init__(self, dimension: int = 384, index_path: str = None):
        self.dimension = dimension
        self.index_path = index_path or Path(__file__).resolve().parent.parent / "vector_store" / "index.faiss"
        self.metadata_path = Path(self.index_path).with_suffix('.pkl')

        if os.path.exists(self.index_path):
            self.index = faiss.read_index(str(self.index_path))
            with open(self.metadata_path, 'rb') as f:
                self.metadata = pickle.load(f)
        else:
            self.index = faiss.IndexFlatL2(dimension)
            self.metadata = []

    def add_vectors(self, vectors: np.ndarray, metadata: list[dict]):
        """Add vectors and their metadata to the index."""
        self.index.add(vectors)
        self.metadata.extend(metadata)

    def search(self, query_vector: np.ndarray, k: int = 5) -> list[tuple[int, float, dict]]:
        """Search for similar vectors and return (index, distance, metadata)."""
        distances, indices = self.index.search(query_vector.reshape(1, -1), k)
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.metadata):
                results.append((int(idx), float(distances[0][i]), self.metadata[idx]))
        return results

    def save(self):
        """Save the index and metadata."""
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        faiss.write_index(self.index, str(self.index_path))
        with open(self.metadata_path, 'wb') as f:
            pickle.dump(self.metadata, f)