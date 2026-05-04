from core.llm import generate_response
from rag.retriever import Retriever

class Generator:
    def __init__(self, retriever: Retriever):
        self.retriever = retriever

    def generate(self, query: str) -> str:
        """Generate a response using retrieved context."""
        relevant_docs = self.retriever.retrieve(query)
        context = "\n\n".join([doc.get('content', '') for doc in relevant_docs])

        if not context.strip():
            return "I'm sorry, I don't have information about that. Can you ask about our menu, policies, or timings?"

        prompt = f"Based on the following information, answer the user's question professionally:\n\n{context}\n\nQuestion: {query}"
        return generate_response(prompt)