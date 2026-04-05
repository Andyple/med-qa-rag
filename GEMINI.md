# Medical Literature Q&A with Uncertainty Quantification

## Project Overview
A RAG system over PubMed abstracts that answers medical/clinical questions and produces
a calibrated confidence score per answer. Built as an AI engineering portfolio project.

## Simplified Project Structure
```
medical-rag/
├── GEMINI.md             # This file (LLM context & instructions)
├── README.md              # Project documentation
├── pyproject.toml         # Python dependencies
├── .env.example           # Environment variable template
├── data/
│   ├── raw/               # PubMed abstracts (gitignored)
│   └── processed/         # chunked, embedded (gitignored)
├── docs/
│   └── archive/           # Complex/enterprise-level docs
├── src/
│   └── medical_rag/
│       ├── main.py        # MVP entry point
│       ├── config.py      # Configuration & thresholds
│       └── core/          # Core RAG components
│           ├── ingestion.py   # Person 1: Fetching & Chunking
│           ├── retrieval.py   # Person 2: Retrieve & Generate
│           └── attribution.py # Person 3: NLI & Uncertainty
└── tests/                 # Unit & integration tests
```

## Stack
- Python 3.11+ (using `uv` or `pip`)
- LangChain (RAG orchestration)
- Chroma (vector store)
- LLM: Local or cloud OpenAI-compatible model
- NLI: `cross-encoder/nli-deberta-v3-small` (for uncertainty/attribution)

## Immediate Goal: MVP Phase 0
1. Build a basic `main.py` that can fetch a single PubMed abstract.
2. Chunk and embed that abstract.
3. Ask a question and get an answer with a basic similarity score.
4. Verify the core pipeline works before layering on complexity.

## Code Style & Standards
- Use type hints on all functions.
- Keep thresholds in `config.py`.
- Prefer simple, readable code over complex abstractions.
- Catch specific exceptions only.

## What NOT to do
- No hardcoded API keys.
- No massive PRs — keep it incremental.
- Don't build the uncertainty aggregation before the retrieval works.
