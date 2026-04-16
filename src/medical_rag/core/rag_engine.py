from typing import List, Dict, Any
from medical_rag.config import settings

"""
RELATIONSHIPS:
- Uses: calls `VectorStoreManager` (from data_pipeline.py) to search for context.
- Used By: The main script (`main.py`) or the API layer (`api.py`) to answer questions.
- Data Flow: 
    1. User Query -> Search (rag_engine.py)
    2. Results -> Prompt Builder (rag_engine.py)
    3. Answer -> Verification (confidence.py)
- Data Contract: Must return the *exact chunks* used to answer the question, as 
  `confidence.py` needs them to verify the claims.
"""

from medical_rag.core.data_pipeline import VectorStoreManager

class RAGOrchestrator:
    """
    Step 1: The "Searcher" & "Answerer".
    """
    def __init__(self):
        """
        Initialize Connection to local llama-server and ChromaDB.
        """
        self.vsm = VectorStoreManager()
        # Additional setup for LLM will go here

    def retrieve_context(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Implement search against the ChromaDB.
        """
        results = self.vsm.vector_store.similarity_search_with_relevance_scores(query, k=k)
        
        context_chunks = []
        for doc, score in results:
            context_chunks.append({
                "text": doc.page_content,
                "metadata": doc.metadata,
                "similarity_score": score
            })
        return context_chunks

    def generate_answer(self, query: str, context_chunks: List[str]) -> str:
        """
        TODO: The Prompt.
        - Template: "You are a medical assistant. Use the following context to answer 
          the question. If you don't know, say you don't know. Context: {context} 
          Question: {query}"
        - Output: The raw string response from the LLM.
        """
        pass

    def generate_with_self_consistency(self, query: str, context_chunks: List[str], n: int = 3) -> Dict[str, Any]:
        """
        TODO: Self-Consistency (Phase 5).
        - Logic: Call generate_answer() N times.
        - Benefit: If 3 out of 3 answers are identical, the 'agreement_score' is 1.0. 
          This is a key input for Person 3's Uncertainty score.
        """
        pass
