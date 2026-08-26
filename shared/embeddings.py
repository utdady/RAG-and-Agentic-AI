"""Local embedding helpers (no API key)."""

from __future__ import annotations

import os
from functools import lru_cache

DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def resolve_embedding_model() -> str:
    return (
        os.getenv("EMBEDDING_MODEL", "").strip()
        or DEFAULT_EMBEDDING_MODEL
    )


@lru_cache(maxsize=1)
def get_embedding_model():
    """
    HuggingFace sentence-transformers embeddings for FAISS / RAG.
    Override with EMBEDDING_MODEL=...
    """
    from langchain_huggingface import HuggingFaceEmbeddings

    model_name = resolve_embedding_model()
    return HuggingFaceEmbeddings(
        model_name=model_name,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )
