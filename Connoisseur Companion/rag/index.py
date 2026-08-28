"""Build Chroma vector indexes from Module 1 structured data (Module 2 lab)."""

from __future__ import annotations

from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
CHROMA_DIR = HERE / "chroma_db"


def _restaurant_document(r: dict) -> str:
    sigs = ", ".join(r.get("signatures") or [])
    return (
        f"{r['name']} in {r['location']}. "
        f"Cuisine: {r['cuisine']}. Rating: {r.get('rating')}/5. "
        f"Price: {r.get('price_range')}. Vibe: {r.get('vibe')}. "
        f"Signatures: {sigs}. {r.get('description', '')}"
    )


def _recipe_document(rec: dict) -> str:
    ingredients = ", ".join(rec.get("ingredients") or [])[:400]
    return (
        f"{rec.get('name', 'Recipe')}. Cuisine: {rec.get('cuisine', 'N/A')}. "
        f"Prep: {rec.get('prep_time', 'N/A')}. {rec.get('image_description', '')} "
        f"Ingredients: {ingredients}"
    )


def build_indexes(force: bool = False) -> Path:
    """
    Persist restaurant + recipe collections under chroma_db/.
    Requires: pip install langchain-chroma sentence-transformers
    """
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    marker = CHROMA_DIR / ".built"
    if marker.exists() and not force:
        return CHROMA_DIR

    from langchain_chroma import Chroma
    from langchain_core.documents import Document
    from langchain_community.embeddings import HuggingFaceEmbeddings

    import sys

    sys.path.insert(0, str(HERE))
    from data_loader import load_recipes, load_restaurants

    embedder = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    restaurants = load_restaurants()
    recipes = load_recipes()[:120]

    rest_docs = [
        Document(
            page_content=_restaurant_document(r),
            metadata={
                "doc_id": f"rest_{i}",
                "source": "restaurant",
                "name": r["name"],
                "location": r["location"],
                "cuisine": r["cuisine"],
            },
        )
        for i, r in enumerate(restaurants)
    ]

    recipe_docs = [
        Document(
            page_content=_recipe_document(rec),
            metadata={
                "doc_id": f"recipe_{i}",
                "source": "recipe",
                "name": rec.get("name", f"recipe_{i}"),
                "cuisine": rec.get("cuisine", "N/A"),
            },
        )
        for i, rec in enumerate(recipes)
    ]

    Chroma.from_documents(
        rest_docs,
        embedder,
        collection_name="restaurant_articles",
        persist_directory=str(CHROMA_DIR),
    )
    Chroma.from_documents(
        recipe_docs,
        embedder,
        collection_name="food_recipes",
        persist_directory=str(CHROMA_DIR),
    )

    marker.write_text("ok", encoding="utf-8")
    return CHROMA_DIR


if __name__ == "__main__":
    path = build_indexes(force="--force" in __import__("sys").argv)
    print(f"Indexes built at {path}")
