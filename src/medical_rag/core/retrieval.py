from typing import List, Dict, Any
from medical_rag.config import settings

"""
RELATIONSHIPS:
- Uses: calls `VectorStoreManager` (from ingestion.py) to search for context.
- Used By: The main script (`main.py`) or the API layer (`api.py`) to answer questions.
- Data Flow: 
    1. User Query -> Search (retrieval.py)
    2. Results -> Prompt Builder (retrieval.py)
    3. Answer -> Verification (attribution.py)
- Data Contract: Must return the *exact chunks* used to answer the question, as 
  `attribution.py` needs them to verify the claims.
"""

class RAGOrchestrator:
    """
    Step 1: The "Searcher" & "Answerer".
    """
    def __init__(self):
        """
        TODO: Initialize Connection to local llama-server.
        - Dependency: Use 'langchain_openai' (configured for local URL) or 'openai' directly.
        - Setup: Set model_name via settings.get_actual_llm_model().
        """
        pass

    def retrieve_context(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        TODO: Implement search against the ChromaDB.
        - Call: Use VectorStoreManager's search method.
        - Results: Must include the 'text' of the chunk and its 'similarity_score'.
        """
        pass

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
