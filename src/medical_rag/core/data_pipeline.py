from typing import List, Dict, Any
from medical_rag.config import settings

"""
RELATIONSHIPS:
- Used By: This script is typically run as a standalone "ingestion job" or called by a 
  setup script to populate the database.
- Outputs To: The `VectorStoreManager` here creates the ChromaDB collection that 
  `rag_engine.py` will later search through.
- Data Contract: Must provide clean, chunked strings and consistent metadata 
  (like PubMed IDs) so the Trust Lead (confidence.py) can trace facts back to sources.
"""

class PubMedIngestor:
    """
    Step 1: The "Fetcher". Connects to NCBI E-Utilities.
    """
    def __init__(self, api_key: str = settings.ncbi_api_key):
        self.api_key = api_key

    def fetch_by_id(self, pubmed_id: str) -> Dict[str, Any]:
        """
        TODO: Implement NCBI E-utilities call.
        - Dependency: Needs 'requests' library.
        - Process: 
            1. Call E-Fetch API with pubmed_id.
            2. Parse XML/JSON response for Title and Abstract.
        - Returns: {'title': str, 'abstract': str, 'id': str}
        """
        pass

    def chunk_text(self, text: str, chunk_size: int = 512) -> List[str]:
        """
        TODO: Implement Text Splitting.
        - Why: LLMs have "context windows". We can't send a whole textbook at once.
        - Logic: Split by paragraph, then sub-split by sentence if a paragraph is > 512 tokens.
        - Output: List of strings to be sent to VectorStoreManager.
        """
        pass

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

class VectorStoreManager:
    """
    Step 2: The "Librarian". Stores chunks so they can be searched by meaning.
    """
    def __init__(self):
        """
        Initialize ChromaDB with local embeddings.
        """
        self.embeddings = OpenAIEmbeddings(
            base_url=settings.embedding_base_url,
            model=settings.embedding_model,
            openai_api_key=settings.openai_api_key  # Usually not needed for local
        )
        self.vector_store = Chroma(
            collection_name=settings.collection_name,
            embedding_function=self.embeddings,
            persist_directory=settings.chroma_db_path
        )

    def add_documents(self, chunks: List[str], metadatas: List[Dict[str, Any]]) -> None:
        """
        Add documents to ChromaDB.
        """
        self.vector_store.add_texts(texts=chunks, metadatas=metadatas)
        # Note: Chroma >= 0.4.x persists automatically, but we ensure it's handled if needed.
