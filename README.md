# Medical Q&A RAG with Uncertainty Quantification

A RAG (Retrieval-Augmented Generation) system over PubMed abstracts that provides medical/clinical answers with calibrated confidence scores.

## Project Vision
To build a medical assistant that not only provides information but also quantifies its own uncertainty, helping clinicians evaluate the reliability of its responses.

## Current Goal
Build a basic pipeline that can fetch, chunk, and embed a PubMed abstract, then answer a simple question based on that context.

## Setup
1.  **Clone the repository.**
2.  **Initialize with `uv`**:
    ```bash
    # Create virtual environment and install dependencies
    uv venv
    source .venv/bin/activate
    uv pip install -e ".[dev]"
    ```
3.  **Set up your environment variables**:
    ```bash
    cp .env.example .env
    # Edit .env to point to your local llama-server/embedding-server
    ```

## Core Features
- PubMed abstract ingestion via NCBI E-utilities.
- Local vector store with Chroma.
- Uncertainty quantification via NLI (Entailment) scoring.
- Self-consistency sampling for more reliable generation.

## Documentation
- High-level design and historical plans can be found in `docs/archive/`.
- Project instructions and guidelines for AI agents are in `GEMINI.md`.
