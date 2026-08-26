"""DocChat settings (paths + retriever knobs)."""

from __future__ import annotations

from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
CACHE_DIR = HERE / "data" / "cache"
CHROMA_DB_PATH = HERE / "data" / "chroma"
CACHE_EXPIRE_DAYS = 7
VECTOR_SEARCH_K = 4
HYBRID_RETRIEVER_WEIGHTS = [0.4, 0.6]  # BM25, vector
MAX_RESEARCH_LOOPS = 2
