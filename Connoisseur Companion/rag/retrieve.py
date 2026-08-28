"""Similarity retrieval with metadata filtering (Module 2) + keyword fallback."""

from __future__ import annotations

from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
CHROMA_DIR = HERE / "chroma_db"


def _keyword_search(query: str, k: int = 8) -> dict:
    import sys

    sys.path.insert(0, str(HERE))
    from data_loader import load_recipes, load_restaurants

    q = query.lower()
    tokens = [t for t in q.split() if len(t) > 2]

    def score(text: str) -> int:
        text_l = text.lower()
        return sum(1 for t in tokens if t in text_l)

    rest_hits = []
    for r in load_restaurants():
        blob = f"{r['name']} {r['location']} {r['cuisine']} {r.get('vibe', '')} {r.get('description', '')}"
        s = score(blob)
        if s:
            rest_hits.append((s, r))
    rest_hits.sort(key=lambda x: (-x[0], -(x[1].get("rating") or 0)))

    recipe_hits = []
    for rec in load_recipes()[:120]:
        blob = f"{rec.get('name', '')} {rec.get('cuisine', '')} {' '.join(rec.get('ingredients') or [])}"
        s = score(blob)
        if s:
            recipe_hits.append((s, rec))
    recipe_hits.sort(key=lambda x: -x[0])

    return {
        "query": query,
        "mode": "keyword",
        "restaurants": [h[1] for h in rest_hits[:k]],
        "recipes": [
            {
                "name": h[1].get("name"),
                "cuisine": h[1].get("cuisine"),
                "prep_time": h[1].get("prep_time"),
                "summary": (h[1].get("image_description") or "")[:200],
            }
            for h in recipe_hits[:k]
        ],
    }


def _chroma_search(query: str, k: int = 8, location: str | None = None) -> dict | None:
    if not (CHROMA_DIR / ".built").exists():
        return None

    try:
        from langchain_chroma import Chroma
        from langchain_community.embeddings import HuggingFaceEmbeddings
    except ImportError:
        return None

    embedder = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    where = {"location": location} if location else None
    rest_db = Chroma(
        collection_name="restaurant_articles",
        persist_directory=str(CHROMA_DIR),
        embedding_function=embedder,
    )
    recipe_db = Chroma(
        collection_name="food_recipes",
        persist_directory=str(CHROMA_DIR),
        embedding_function=embedder,
    )

    rest_kwargs = {"k": k}
    if where:
        rest_kwargs["filter"] = where

    rest_res = rest_db.similarity_search_with_score(query, **rest_kwargs)
    recipe_res = recipe_db.similarity_search_with_score(query, k=k)

    restaurants = []
    for doc, _score in rest_res:
        restaurants.append(
            {
                "name": doc.metadata.get("name"),
                "location": doc.metadata.get("location"),
                "cuisine": doc.metadata.get("cuisine"),
                "snippet": doc.page_content[:240],
            }
        )

    recipes = []
    for doc, _score in recipe_res:
        recipes.append(
            {
                "name": doc.metadata.get("name"),
                "cuisine": doc.metadata.get("cuisine"),
                "summary": doc.page_content[:240],
            }
        )

    return {
        "query": query,
        "mode": "chroma",
        "restaurants": restaurants,
        "recipes": recipes,
    }


def search_knowledge(
    query: str,
    k: int = 8,
    location: str | None = None,
) -> dict:
    """Top-level retrieval used by MCP tools and the multi-agent workflow."""
    chroma_result = _chroma_search(query, k=k, location=location)
    if chroma_result and (chroma_result["restaurants"] or chroma_result["recipes"]):
        return chroma_result
    return _keyword_search(query, k=k)
