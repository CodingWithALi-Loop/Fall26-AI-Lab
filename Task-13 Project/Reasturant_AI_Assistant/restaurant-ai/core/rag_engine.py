from pathlib import Path
from rag.embeddings import EmbeddingModel
from rag.retriever import Retriever
from rag.generator import Generator
from core.vector_db import VectorDatabase

class RAGEngine:
    def __init__(self):
        self.embedding_model = EmbeddingModel()
        self.vector_db = VectorDatabase(dimension=384)
        self.retriever = Retriever(self.embedding_model, self.vector_db)
        self.generator = Generator(self.retriever)
        self.documents_loaded = False
        self._load_documents()

    def _load_documents(self):
        """Load and index documents from data folder."""
        if self.documents_loaded:
            return

        try:
            data_dir = Path(__file__).resolve().parent.parent / "data"
            documents = []

            for file_path in data_dir.glob("*.txt"):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        # Split into chunks (simple paragraph splitting)
                        chunks = [chunk.strip() for chunk in content.split('\n\n') if chunk.strip()]
                        for chunk in chunks:
                            documents.append({
                                'content': chunk,
                                'source': file_path.name
                            })

            if documents:
                texts = [doc['content'] for doc in documents]
                embeddings = self.embedding_model.encode(texts)
                self.vector_db.add_vectors(embeddings, documents)
                self.vector_db.save()
                self.documents_loaded = True
        except Exception as e:
            print(f"Warning: Failed to load documents for RAG: {e}")
            self.documents_loaded = False

    def query(self, question: str) -> str:
        """Answer a question using RAG."""
        try:
            self._load_documents()
            if not self.documents_loaded:
                return "I'm sorry, I don't have information about that right now. Can you ask about our menu or ordering?"
            return self.generator.generate(question)
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}"