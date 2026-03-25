# Architectural Decisions & Design Rationale

> Medical Literature Q&A with Uncertainty Quantification

## 1. System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    API Layer (FastAPI)                            │
│                    /ask endpoint                                  │
└─────────────────────────────────────────────────────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Core Pipeline                                  │
│  ┌──────────┬──────────┬──────────┬──────────┬───────────────┐  │
│  │ Ingest   │ Retrieve │ Conflict │ Generate │ Uncertainty   │  │
│  │          │          │ Detect   │         │ Aggregation    │  │
│  └──────────┴──────────┴──────────┴──────────┴───────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    External Services                              │
│  • NCBI E-utilities (abstracts)     • Chroma (vector store)       │
│  • OpenAI/embeddings                • Claude (LLM)                │
│  • HuggingFace (NLI model)          • spaCy (NLP)                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Key Architectural Decisions

### Decision 1: Modular Layered Architecture

**Why:** The pipeline has distinct phases with clear inputs/outputs. Separation enables:
- Independent testing of each component
- Easy swapping of implementations (e.g., different vector stores)
- Parallel development

**Anti-pattern avoided:** Monolithic `run()` function that chains everything together.

**Implementation:** Each layer exposes a single interface:
```python
# Ingestion exposes
IngestionResult: {
    chunks: List[Chunk],      # text + metadata
    total_count: int,
    ingestion_time: float
}

# Retrieval exposes
RetrievalResult: {
    chunks: List[RetrievedChunk],  # with similarity scores
    query: str,
    k: int
}
```

---

### Decision 2: Explicit Uncertainty Signals at Each Layer

**Why:** The uncertainty aggregation layer needs clean, well-defined signals from downstream components. Mixing signals makes calibration impossible.

**Signals defined:**
| Layer | Signal | Meaning |
|-------|--------|---------|
| Retrieval | Mean similarity score | How close are chunks to query? |
| Generation | Agreement rate | How consistent are N LLM responses? |
| Attribution | Support fraction | What % of claims have evidence? |

**Anti-pattern avoided:** "Black box" confidence from the LLM alone.

---

### Decision 3: Configurable Thresholds

**Why:** Thresholds (contradiction, support, uncertainty) should be:
- Tunable on eval data
- Documented for reproducibility
- Not hardcoded

**Implementation:**
```python
# config.py
class Thresholds:
    CONTRADICTION_THRESHOLD = 0.70   # trigger flag
    SUPPORT_THRESHOLD = 0.65         # claim considered supported
    UNSUPPORTED_FLAG = "UNSUPPORTED" # marker for low-confidence claims
```

**Trade-off:** Fixed thresholds reduce flexibility, but make results reproducible and easier to interpret.

---

### Decision 4: Self-Consistency with Semantic Agreement

**Why:** Exact string matching fails for paraphrased medical answers. Semantic similarity allows:
- "Myocardial infarction" ≈ "heart attack"
- Different but equivalent formulations

**Implementation:**
```python
# Use sentence embeddings to compare N responses
# Agreement = mean cosine similarity across all pairs
```

**Anti-pattern avoided:** Exact string matching (too brittle for medical terminology).

---

### Decision 5: Claim-Level Attribution

**Why:** Sentence-level attribution is too coarse for medical claims. Claims often span multiple sentences (e.g., "Patients with hypertension AND diabetes should..."), while NLI needs a single hypothesis.

**Implementation:**
1. Split answer into claims using spaCy sentence splitter
2. Each claim gets NLI score against each chunk
3. Best chunk + score reported for each claim
4. Claim flagged UNSUPPORTED if best score < threshold

**Trade-off:** More computational cost, but significantly better accuracy.

---

### Decision 6: CPU-First Design

**Why:** Many users will run this locally without GPU. The NLI model and embeddings are heavy operations.

**Implementation:**
```python
# Graceful CPU fallback for all heavy models
# Use torch.cpu if cuda not available
# Batch smaller on CPU to stay within memory
```

**Anti-pattern avoided:** Assuming GPU availability (breaks local development).

---

### Decision 7: Structured JSON Outputs

**Why:** LLM outputs need to be parsed reliably. Medical information must be captured accurately.

**Implementation:**
```json
{
  "answer": "String",
  "agreement_score": 0.92,
  "confidence": {
    "retrieval": 0.85,
    "generation": 0.92,
    "attribution": 0.78
  },
  "flags": {
    "has_unsupported_claims": false,
    "has_contradictions": true
  },
  "sources": [
    {
      "chunk_id": "chunk_12345",
      "similarity": 0.89,
      "nli_scores": [0.82, 0.76, 0.81]
    }
  ]
}
```

**Anti-pattern avoided:** Relying on free-format text that needs regex parsing.

---

## 3. Data Flow

```
1. INGESTION
   ┌─────────────────────────────────────────────────┐
   │ Query (MeSH term/keyword)                        │
   │ ────────────────────────────► NCBI E-utilities   │
   │ Response (abstracts) ───────────────────────────► Chunker
   │ Chunks ─────────────────────────────────────────► Embedder
   │ Embeddings ─────────────────────────────────────► Chroma
   └─────────────────────────────────────────────────┘

2. RETRIEVAL
   ┌─────────────────────────────────────────────────┐
   │ User Query ─────────────────────────────────────► Chroma
   │ Top-k chunks + similarity scores ───────────────► Pipeline
   └─────────────────────────────────────────────────┘

3. CONFLICT DETECTION
   ┌─────────────────────────────────────────────────┐
   │ Chunk pairs ────────────────────────────────────► NLI Model
   │ Contradiction scores ───────────────────────────► Flag if > threshold
   └─────────────────────────────────────────────────┘

4. GENERATION
   ┌─────────────────────────────────────────────────┐
   │ Query + Top-k chunks ───────────────────────────► Claude
   │ N samples (self-consistency) ───────────────────► Agreement score
   └─────────────────────────────────────────────────┘

5. ATTRIBUTION
   ┌─────────────────────────────────────────────────┐
   │ Answer ─────► Claim splitter ──────────────────► Claims
   │ Chunks ─────────────────────────────────────────► NLI Model
   │ Each claim + chunk ────────────────────────────► Best score
   └─────────────────────────────────────────────────┘

6. UNCERTAINTY AGGREGATION
   ┌─────────────────────────────────────────────────┐
   │ Signals from all layers ───────────────────────► Weighted avg
   │ Weights from config ───────────────────────────► Final score
   └─────────────────────────────────────────────────┘
```

---

## 4. Component Interfaces

### Ingestion Layer

**Input:** `MeSHQuery` or `KeywordQuery`

**Output:** `IngestionResult`

**Key functions:**
```python
def fetch_abstracts(query: str, limit: int) -> List[Abstract]:
    """Fetch PubMed abstracts via NCBI E-utilities"""

def chunk_texts(texts: List[str], max_tokens: int = 512) -> List[Chunk]:
    """Paragraph-first, sentence-boundary fallback"""

def embed_chunks(chunks: List[Chunk]) -> List[EmbeddedChunk]:
    """Create vector representations"""

def store_in_chroma(chunks: List[EmbeddedChunk]) -> None:
    """Add to vector store"""
```

### Retrieval Layer

**Input:** `RetrievalRequest`

**Output:** `RetrievalResult`

**Key functions:**
```python
def retrieve(query: str, k: int = 5) -> List[RetrievedChunk]:
    """Return top-k chunks with cosine similarity scores"""

def filter_by_similarity(chunks: List[RetrievedChunk], min_sim: float) -> List[RetrievedChunk]:
    """Optional: filter out low-similarity chunks"""
```

### Conflict Detection Layer

**Input:** `List[RetrievedChunk]`

**Output:** `ConflictStatus` (boolean flag)

**Key functions:**
```python
def compute_pairwise_nli(chunks: List[RetrievedChunk]) -> List[Tuple[ChunkId, ChunkId, float]]:
    """Score all pairs for contradiction"""

def has_contradictions(scores: List[float], threshold: float = 0.70) -> bool:
    """Return True if any pair exceeds threshold"""
```

### Generation Layer

**Input:** `GenerationRequest` (query + context)

**Output:** `GenerationResult` (answer + agreement score)

**Key functions:**
```python
def generate_single(query: str, context: List[str]) -> str:
    """Single LLM call with structured JSON output"""

def generate_with_consistency(n_samples: int = 3) -> Tuple[str, float]:
    """Run N times, compute semantic agreement"""

def compute_agreement(responses: List[str]) -> float:
    """Mean cosine similarity across all pairs"""
```

### Attribution Layer

**Input:** `AttributionRequest` (answer + chunks)

**Output:** `AttributionResult` (claims + support status)

**Key functions:**
```python
def split_into_claims(text: str) -> List[str]:
    """Use spaCy sentencizer"""

def score_claim_against_chunks(
    claim: str, 
    chunks: List[RetrievedChunk]
) -> List[Tuple[ChunkId, float]]:
    """NLI scoring per claim-chunk pair"""

def get_best_support(
    claim: str, 
    chunks: List[RetrievedChunk]
) -> Tuple[ChunkId, float]:
    """Return chunk with highest entailment score"""
```

### Uncertainty Aggregation Layer

**Input:** `UncertaintyRequest` (all signals)

**Output:** `UncertaintyResult` (final score + flags)

**Key functions:**
```python
def compute_retrieval_confidence(chunks: List[RetrievedChunk]) -> float:
    """Mean cosine similarity of top-k chunks"""

def compute_generation_confidence(responses: List[str]) -> float:
    """Agreement rate across N samples"""

def compute_attribution_confidence(claims: List[Claim], nli_scores: List[float]) -> float:
    """Fraction with score >= SUPPORT_THRESHOLD"""

def aggregate(
    retrieval_conf: float,
    generation_conf: float,
    attribution_conf: float
) -> float:
    """Weighted average; weights in config"""
```

---

## 5. Error Handling Strategy

### Failure Modes & Mitigations

| Failure | Impact | Mitigation |
|---------|--------|------------|
| NCBI rate limit | Can't fetch data | Exponential backoff, cache recently fetched IDs |
| LLM timeout | No answer | Timeout after 60s, retry with smaller context |
| NLI model OOM | Can't detect conflicts | Smaller batch size, CPU fallback |
| Chunk too long | Embedding fails | Sentence boundary fallback |
| No relevant chunks found | Low retrieval score | Return with warning, don't crash |

### Error Boundaries

Each layer should:
1. Catch only its own failures
2. Never re-raise uncaught exceptions
3. Log errors with context (query, timestamp, stage)
4. Return structured error info to caller

---

## 6. Performance Considerations

### Current Bottlenecks (estimated)

1. **NLI pairwise scoring**: O(n²) pairs for n chunks
   - Mitigation: Limit to top-10 chunks for conflict detection

2. **Self-consistency sampling**: N × LLM calls
   - Mitigation: N=3 minimum (portfolio demo doesn't need N=10)

3. **NCBI rate limits**: ~3 calls/second
   - Mitigation: Batch queries, cache by MeSH term

### Future Optimization Paths

1. **Hybrid retrieval**: Keyword + vector search
2. **Approximate nearest neighbors** (FAISS) for faster retrieval
3. **Model quantization** for CPU-friendly inference

---

## 7. Extensibility Points

### Swappable Components

| Component | Current | Alternatives |
|-----------|---------|-------------|
| Vector Store | Chroma | Qdrant, FAISS, Pinecone |
| Embeddings | text-embedding-3-small | PubMedBERT, multilingual-e5 |
| NLI Model | nli-deberta-v3-small | cross-encoder/ms-marco-MiniLM-L-12-v2 |
| LLM | Claude | OpenAI, local Ollama |
| Chunking | Paragraph-first | Recursive character, fixed-size |

All alternatives should require minimal code changes.

---

## 8. Testing Strategy

### Unit Tests (per layer)

- Mock external calls (NCBI, LLM, NLI)
- Test edge cases (empty input, malformed text)
- Verify output schema matches spec

### Integration Tests

- End-to-end pipeline with synthetic data
- Verify signals propagate correctly
- Check uncertainty aggregation math

### Evals

- BioASQ dataset: measure calibration
- Retrieval recall: did correct chunk appear?
- Confidence-accuracy plots

---

## 9. Key Metrics to Track

| Metric | Target | Why |
|--------|--------|-----|
| Retrieval recall@5 | > 0.6 | Correct chunk in top-5 |
| Calibration error | < 0.15 | Predicted confidence ≈ actual accuracy |
| Agreement rate | 0.7–0.95 | Suggests reliable answer |
| Attribution support | > 80% | Most claims backed by evidence |

---

## 10. Red Flags (Anti-Patterns to Avoid)

1. ❌ **Hardcoding thresholds** → All in `config.py`
2. ❌ **Swallowing LLM errors** → Propagate with context
3. ❌ **Treating all chunks equally** → Use similarity scores
4. ❌ **Ignoring retrieval confidence** → It's a valid signal
5. ❌ **Single-shot generation** → Self-consistency is cheap
6. ❌ **No caching** → NCBI and LLM calls are expensive

---

*Generated: 2026-03-23*
*Version: 1.0 (pre-implementation)*
