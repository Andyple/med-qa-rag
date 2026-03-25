from medical_rag.config import settings

def main() -> None:
    # MVP Entry point: Verifying connection to local servers
    print("--- Medical RAG MVP Setup ---")

    # Detect models
    llm_model = settings.get_actual_llm_model()
    print(f"LLM Server: {settings.llm_base_url}")
    print(f"Detected LLM Model: {llm_model}")

    print(f"Embedding Server: {settings.embedding_base_url}")
    print(f"Embedding Model: {settings.embedding_model}")

    # Next steps for MVP implementation...
    print("\nNext Step: Implement PubMed fetcher & basic vector store.")

if __name__ == "__main__":
    main()
