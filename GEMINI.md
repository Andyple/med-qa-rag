# Medical Literature Q&A with Uncertainty Quantification

## Project overview
RAG system over PubMed abstracts that answers medical/clinical questions and produces
a calibrated confidence score per answer. Built as an AI engineering portfolio project.

## Stack
- Python 3.11+ with uv
- LangChain or LlamaIndex for RAG orchestration (decide early and stick with it)
- Chroma or Qdrant for vector store
- Embedding model: `text-embedding-3-small` (baseline) or PubMedBERT embeddings (preferred)
- NLI model: `cross-encoder/nli-deberta-v3-small` via HuggingFace transformers
- LLM: Claude via Anthropic SDK (`claude-sonnet-4-20250514`)
- spaCy for sentence splitting
- FastAPI for the API layer
- Pytest for all tests

## Project structure
```
medical-rag/
├── AGENTS.md
├── README.md
├── pyproject.toml
├── .env.example
├── docs/
│   ├── architecture.md       # system design decisions
│   ├── eval-results.md       # benchmark outcomes, update as you run evals
│   └── implementation-plan.md
├── data/
│   ├── raw/                  # PubMed abstracts (gitignored)
│   └── processed/            # chunked, embedded (gitignored)
├── src/
│   └── medical_rag/
│       ├── ingestion/        # data loading, chunking, embedding
│       ├── retrieval/        # vector search, reranking
│       ├── generation/       # LLM prompts, self-consistency sampling
│       ├── attribution/      # claim splitting, NLI scoring, conflict detection
│       ├── uncertainty/      # signal aggregation, confidence scoring
│       ├── api/              # FastAPI routes
│       └── eval/             # evaluation harness, BioASQ loader
└── tests/
    ├── unit/
    └── integration/
```

## Commands
- Install deps: `pip install -e ".[dev]"`
- Run tests: `pytest tests/ -v`
- Run API locally: `uvicorn src.medical_rag.api.main:app --reload`
- Ingest corpus: `python -m medical_rag.ingestion.run --limit 50000`
- Run eval: `python -m medical_rag.eval.run --dataset bioasq`
- Type check: `mypy src/`
- Lint: `ruff check src/ tests/`

## Core pipeline (build in this order)
1. Ingestion → chunking → embedding → vector store
2. Retrieval (top-k with similarity scores)
3. Conflict detection across retrieved chunks
4. LLM generation with self-consistency sampling (N=3 minimum)
5. Claim-level attribution via NLI model
6. Uncertainty score aggregation
7. FastAPI wrapper
8. Eval harness

## Uncertainty scoring rules
- Retrieval confidence = mean cosine similarity of top-k chunks to query
- Generation confidence = answer agreement rate across N self-consistency samples
- Attribution confidence = fraction of claims with NLI entailment score ≥ 0.65
- Final score = weighted average; weights tuned on eval set, not hardcoded
- Flag `has_unsupported_claims: true` if any claim scores below threshold
- Flag `has_contradictions: true` if any chunk pair has contradiction score ≥ 0.7

## Code style
- Type hints on all functions
- Docstrings on all public functions (Google style)
- No hardcoded thresholds — all tuneable values go in `config.py`
- All LLM prompts live in `src/medical_rag/generation/prompts.py`, never inline
- Structured outputs (JSON mode) for all LLM calls that return data
- Never catch bare `Exception`; always catch specific exceptions

## What NOT to do
- Do not store API keys in code or commit `.env`
- Do not run the NLI model on GPU without checking availability first (graceful CPU fallback)
- Do not use cosine similarity alone for claim attribution — NLI is required
- Do not skip the eval harness; calibration results are a key resume artifact
