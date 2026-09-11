"""
Shared food dataset + Chroma similarity helpers.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import chromadb
from chromadb.utils import embedding_functions

DEFAULT_EMBED_MODEL = "all-MiniLM-L6-v2"
DATA_DIR = Path(__file__).resolve().parent / "data"
DEFAULT_DATASET = DATA_DIR / "FoodDataSet.json"

_client = chromadb.Client()


def load_food_data(file_path: str | Path | None = None) -> list[dict]:
    path = Path(file_path) if file_path else DEFAULT_DATASET
    try:
        with open(path, encoding="utf-8") as file:
            food_data = json.load(file)

        for i, item in enumerate(food_data):
            item["food_id"] = str(item.get("food_id", i + 1))
            item.setdefault("food_ingredients", [])
            item.setdefault("food_description", "")
            item.setdefault("cuisine_type", "Unknown")
            item.setdefault("food_calories_per_serving", 0)

            features = item.get("food_features")
            if isinstance(features, dict):
                item["taste_profile"] = ", ".join(
                    str(v) for v in features.values() if v
                )
            else:
                item.setdefault("taste_profile", "")

        print(f"Loaded {len(food_data)} food items from {path.name}")
        return food_data
    except Exception as e:
        print(f"Error loading food data: {e}")
        return []


def _embedding_fn(model_name: str = DEFAULT_EMBED_MODEL):
    return embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=model_name
    )


def create_similarity_search_collection(
    collection_name: str,
    collection_metadata: dict | None = None,
    embed_model: str = DEFAULT_EMBED_MODEL,
):
    """Create (or recreate) a Chroma collection with MiniLM embeddings."""
    try:
        _client.delete_collection(collection_name)
    except Exception:
        pass

    ef = _embedding_fn(embed_model)
    meta = {"hnsw:space": "cosine"}
    if collection_metadata:
        meta.update(collection_metadata)

    # Portable create (avoids Chroma 1.x-only configuration= API)
    try:
        return _client.create_collection(
            name=collection_name,
            embedding_function=ef,
            metadata=meta,
        )
    except TypeError:
        return _client.create_collection(
            name=collection_name,
            embedding_function=ef,
        )


def _food_document_text(food: dict) -> str:
    text = f"Name: {food['food_name']}. "
    text += f"Description: {food.get('food_description', '')}. "
    text += f"Ingredients: {', '.join(food.get('food_ingredients', []))}. "
    text += f"Cuisine: {food.get('cuisine_type', 'Unknown')}. "
    text += f"Cooking method: {food.get('cooking_method', '')}. "
    taste = food.get("taste_profile", "")
    if taste:
        text += f"Taste and features: {taste}. "
    benefits = food.get("food_health_benefits", "")
    if benefits:
        text += f"Health benefits: {benefits}. "
    nutrition = food.get("food_nutritional_factors")
    if isinstance(nutrition, dict):
        nutrition_text = ", ".join(f"{k}: {v}" for k, v in nutrition.items())
        text += f"Nutrition: {nutrition_text}."
    return text


def populate_similarity_collection(collection, food_items: list[dict]) -> None:
    documents: list[str] = []
    metadatas: list[dict] = []
    ids: list[str] = []
    used_ids: set[str] = set()

    for i, food in enumerate(food_items):
        base_id = str(food.get("food_id", i))
        unique_id = base_id
        counter = 1
        while unique_id in used_ids:
            unique_id = f"{base_id}_{counter}"
            counter += 1
        used_ids.add(unique_id)

        documents.append(_food_document_text(food))
        ids.append(unique_id)
        metadatas.append(
            {
                "name": food["food_name"],
                "cuisine_type": food.get("cuisine_type", "Unknown"),
                "ingredients": ", ".join(food.get("food_ingredients", [])),
                "calories": int(food.get("food_calories_per_serving", 0) or 0),
                "description": food.get("food_description", ""),
                "cooking_method": food.get("cooking_method", ""),
                "health_benefits": food.get("food_health_benefits", ""),
                "taste_profile": food.get("taste_profile", ""),
            }
        )

    collection.add(documents=documents, metadatas=metadatas, ids=ids)
    print(f"Added {len(food_items)} food items to collection '{collection.name}'")


def _format_hit(results: dict, i: int) -> dict[str, Any]:
    meta = results["metadatas"][0][i]
    distance = results["distances"][0][i]
    return {
        "food_id": results["ids"][0][i],
        "food_name": meta.get("name", ""),
        "food_description": meta.get("description", ""),
        "cuisine_type": meta.get("cuisine_type", "Unknown"),
        "food_calories_per_serving": meta.get("calories", 0),
        "food_ingredients": meta.get("ingredients", ""),
        "food_health_benefits": meta.get("health_benefits", ""),
        "cooking_method": meta.get("cooking_method", ""),
        "taste_profile": meta.get("taste_profile", ""),
        "similarity_score": 1 - distance,
        "distance": distance,
    }


def perform_keyword_search(
    food_items: list[dict],
    query: str,
    n_results: int = 5,
    max_calories: int | None = None,
) -> list[dict]:
    """Lightweight ranked search without MiniLM/Chroma (hub-safe on small RAM)."""
    import re

    q = (query or "").strip().lower()
    if not q or not food_items:
        return []

    if max_calories is None:
        m = re.search(
            r"(?:under|below|less than|max(?:imum)?)\s*(\d+)\s*(?:cal)?",
            q,
        )
        if m:
            max_calories = int(m.group(1))
        else:
            m = re.search(r"(\d+)\s*(?:calories|cals|kcal)\b", q)
            if m:
                max_calories = int(m.group(1))

    stop = {
        "with",
        "that",
        "this",
        "from",
        "have",
        "want",
        "like",
        "some",
        "under",
        "below",
        "than",
        "less",
        "more",
        "calories",
        "calorie",
        "cals",
        "kcal",
        "food",
        "meal",
        "please",
        "find",
        "show",
        "give",
    }
    tokens = [
        t
        for t in re.findall(r"[a-z0-9]+", q)
        if len(t) > 2 and t not in stop and not t.isdigit()
    ]
    if not tokens:
        tokens = [t for t in re.findall(r"[a-z0-9]+", q) if len(t) > 1]

    scored: list[tuple[float, dict]] = []
    for food in food_items:
        cals = int(food.get("food_calories_per_serving", 0) or 0)
        if max_calories is not None and cals > max_calories:
            continue

        name = str(food.get("food_name", "")).lower()
        cuisine = str(food.get("cuisine_type", "")).lower()
        taste = str(food.get("taste_profile", "")).lower()
        blob = _food_document_text(food).lower()
        score = 0.0
        matched = 0
        for t in tokens:
            hit = False
            if t in name:
                score += 4.0
                hit = True
            if t in taste or t in cuisine:
                score += 2.5
                hit = True
            if t in blob:
                score += 1.0
                hit = True
            if hit:
                matched += 1
        if matched == 0:
            continue
        # Prefer multi-token matches (spicy + healthy beats one weak hit).
        score += matched * 1.5
        if any(w in q for w in ("healthy", "light", "diet", "low")) and cals > 0:
            score += max(0.0, (500 - min(cals, 500)) / 500.0)
        if "dinner" in q or "lunch" in q or "meal" in q:
            # Downrank obvious snacks/desserts/nuts.
            snackish = ("cookie", "macaroon", "seed", "peanut", "chip", "candy", "cake")
            if any(s in name for s in snackish):
                score *= 0.35

        scored.append(
            (
                score,
                {
                    "food_id": str(food.get("food_id", "")),
                    "food_name": food.get("food_name", ""),
                    "food_description": food.get("food_description", ""),
                    "cuisine_type": food.get("cuisine_type", "Unknown"),
                    "food_calories_per_serving": cals,
                    "food_ingredients": ", ".join(food.get("food_ingredients", []) or []),
                    "food_health_benefits": food.get("food_health_benefits", ""),
                    "cooking_method": food.get("cooking_method", ""),
                    "taste_profile": food.get("taste_profile", ""),
                    "similarity_score": min(score / (6.0 * max(len(tokens), 1)), 1.0),
                    "distance": 0.0,
                },
            )
        )

    scored.sort(key=lambda pair: (-pair[0], pair[1]["food_calories_per_serving"]))
    return [hit for _, hit in scored[:n_results]]


def perform_filtered_similarity_search(
    collection,
    query: str,
    cuisine_filter: str | None = None,
    max_calories: int | None = None,
    n_results: int = 5,
) -> list[dict]:
    filters: list[dict] = []
    if cuisine_filter:
        filters.append({"cuisine_type": cuisine_filter})
    if max_calories is not None:
        filters.append({"calories": {"$lte": int(max_calories)}})

    where_clause = None
    if len(filters) == 1:
        where_clause = filters[0]
    elif len(filters) > 1:
        where_clause = {"$and": filters}

    try:
        kwargs: dict[str, Any] = {
            "query_texts": [query],
            "n_results": n_results,
        }
        if where_clause is not None:
            kwargs["where"] = where_clause
        results = collection.query(**kwargs)
        if not results or not results["ids"] or not results["ids"][0]:
            return []
        return [_format_hit(results, i) for i in range(len(results["ids"][0]))]
    except Exception as e:
        print(f"Error in filtered search: {e}")
        return []
