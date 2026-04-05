from typing import List, Dict, Any
from medical_rag.config import settings

"""
RELATIONSHIPS:
- Uses: Takes inputs from `retrieval.py` (the Answer + the Chunks).
- Used By: The final RAG pipeline to "grade" the LLM's answer before showing it.
- Data Flow: 
    1. Answer (from retrieval.py) -> Claim Splitter
    2. Each Claim -> NLI Scorer (against chunks from retrieval.py)
    3. Scores -> UncertaintyAggregator -> Final Confidence.
- Data Contract: Must return a structured report showing which sentences in the 
  answer are backed by evidence and which aren't.
"""

class AttributionModel:
    """
    Step 1: The "Fact Checker".
    """
    def __init__(self, model_name: str = "cross-encoder/nli-deberta-v3-small"):
        """
        TODO: Load the NLI Model.
        - Dependency: Use 'transformers' library.
        - Device: Check if CUDA (GPU) is available, else use 'cpu'.
        """
        pass

    def split_into_claims(self, text: str) -> List[str]:
        """
        TODO: Claim Extraction.
        - Why: A medical answer might have 3 true facts and 1 false fact. 
          We need to verify them individually.
        - Tool: Use spaCy's 'en_core_sci_sm' or 'en_core_web_sm' for sentence splitting.
        """
        pass

    def score_claim(self, claim: str, chunks: List[str]) -> Dict[str, Any]:
        """
        TODO: NLI Scoring.
        - Process: 
            For each chunk:
                Run NLI: (Premise = Chunk, Hypothesis = Claim)
                Get 'Entailment' score (0.0 to 1.0).
            Keep the highest score.
        - Result: {'claim': str, 'best_chunk': str, 'score': float}
        """
        pass

class UncertaintyAggregator:
    """
    Step 2: The "Confidence Meter".
    """
    def compute_final_score(
        self,
        retrieval_score: float,
        generation_agreement: float,
        attribution_score: float
    ) -> float:
        """
        TODO: Weighted Scoring (Phase 7).
        - Formula: Confidence = (W1 * Ret) + (W2 * Gen) + (W3 * Attr)
        - Output: A final percentage (e.g. 85%) for the user to see.
        """
        pass
