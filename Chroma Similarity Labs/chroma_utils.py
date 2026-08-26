"""Portable Chroma helpers for the similarity labs."""

from __future__ import annotations

import chromadb
from chromadb.utils import embedding_functions

DEFAULT_EMBED_MODEL = "all-MiniLM-L6-v2"

_client = chromadb.Client()


def get_client():
    return _client


def embedding_fn(model_name: str = DEFAULT_EMBED_MODEL):
    return embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=model_name
    )


def create_collection(
    name: str,
    description: str = "",
    embed_model: str = DEFAULT_EMBED_MODEL,
):
    """Create or recreate a collection with MiniLM + cosine space."""
    try:
        _client.delete_collection(name)
    except Exception:
        pass

    ef = embedding_fn(embed_model)
    meta = {"hnsw:space": "cosine"}
    if description:
        meta["description"] = description

    try:
        return _client.create_collection(
            name=name,
            embedding_function=ef,
            metadata=meta,
        )
    except TypeError:
        return _client.create_collection(
            name=name,
            embedding_function=ef,
        )


def print_query_hits(results, query_label: str, n: int = 3) -> None:
    if not results or not results.get("ids") or not results["ids"][0]:
        print(f'No documents found similar to "{query_label}"')
        return
    print(f'Top hits for "{query_label}":')
    for i in range(min(n, len(results["ids"][0]))):
        doc_id = results["ids"][0][i]
        score = results["distances"][0][i]
        text = results["documents"][0][i]
        meta = results["metadatas"][0][i] if results.get("metadatas") else {}
        print(f"  {i + 1}. id={doc_id} distance={score:.4f}")
        if text:
            print(f"     text: {text[:120]}{'...' if len(text) > 120 else ''}")
        if meta:
            print(f"     meta: {meta}")
