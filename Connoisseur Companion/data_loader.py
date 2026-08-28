"""Load and normalize Module 1 California dining data."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA_DIR = HERE / "data"

CULINARY_MAP_PATH = DATA_DIR / "California-Culinary-Map.txt"
RESTAURANTS_PATH = DATA_DIR / "structured_restaurant_data.json"
REVIEWS_PATH = DATA_DIR / "augmented_user_review.json"
RECIPES_PATH = DATA_DIR / "augmented_food_recipe.json"


def _read_json(path: Path) -> list | dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _price_label(value) -> str:
    if value is None:
        return "N/A"
    if isinstance(value, str):
        return value
    try:
        n = int(value)
        return "$" * max(1, min(n, 4))
    except (TypeError, ValueError):
        return str(value)


def normalize_restaurant(raw: dict) -> dict:
    """Unify M1 schema for MCP tools, RAG, and agents."""
    vibe = raw.get("vibe") or raw.get("ambiance") or ""
    vibes = raw.get("vibes")
    if not vibes and vibe:
        vibes = [v.strip() for v in str(vibe).replace("/", ",").split(",") if v.strip()]
    elif isinstance(vibes, str):
        vibes = [vibes]

    location = raw.get("location") or raw.get("neighborhood") or "N/A"
    cuisine = raw.get("cuisine") or raw.get("food_style") or "N/A"
    signatures = raw.get("signatures") or raw.get("specialties") or []

    parts = [
        raw.get("type", ""),
        raw.get("environment", ""),
        raw.get("description", ""),
    ]
    description = " ".join(p for p in parts if p).strip() or raw.get("environment", "")

    return {
        "itemId": raw.get("itemId") or raw.get("id"),
        "name": raw.get("name", "Unknown"),
        "location": location,
        "neighborhood": location,
        "cuisine": cuisine,
        "food_style": raw.get("food_style") or cuisine,
        "rating": raw.get("rating"),
        "price_range": _price_label(raw.get("price_range")),
        "vibe": vibe,
        "vibes": vibes or [],
        "signatures": signatures,
        "description": description,
        "type": raw.get("type", ""),
        "environment": raw.get("environment", ""),
    }


def normalize_review(raw: dict, restaurants_by_id: dict[int, dict]) -> dict:
    item_id = raw.get("itemId")
    restaurant = restaurants_by_id.get(item_id, {})
    name = restaurant.get("name", "Unknown")

    captions = raw.get("image_captions") or []
    image_description = "; ".join(captions) if captions else raw.get("image_description", "N/A")

    return {
        "restaurant_name": name,
        "itemId": item_id,
        "reviewer": raw.get("userId", "anonymous"),
        "title": raw.get("title", ""),
        "rating": raw.get("rating"),
        "review_text": raw.get("text") or raw.get("review_text", ""),
        "visit_date": raw.get("date") or raw.get("visit_date", "N/A"),
        "image_description": image_description,
    }


@lru_cache(maxsize=1)
def load_restaurants() -> list[dict]:
    raw_list = _read_json(RESTAURANTS_PATH)
    return [normalize_restaurant(r) for r in raw_list]


@lru_cache(maxsize=1)
def restaurants_by_item_id() -> dict[int, dict]:
    out: dict[int, dict] = {}
    for r in load_restaurants():
        item_id = r.get("itemId")
        if item_id is not None:
            out[int(item_id)] = r
    return out


@lru_cache(maxsize=1)
def load_reviews() -> list[dict]:
    raw_list = _read_json(REVIEWS_PATH)
    by_id = restaurants_by_item_id()
    return [normalize_review(r, by_id) for r in raw_list]


@lru_cache(maxsize=1)
def load_recipes() -> list[dict]:
    return _read_json(RECIPES_PATH)


@lru_cache(maxsize=1)
def load_culinary_map() -> str:
    return CULINARY_MAP_PATH.read_text(encoding="utf-8")


def find_restaurants_by_name(query: str) -> list[dict]:
    q = query.lower().strip()
    if not q:
        return []
    matches = []
    for r in load_restaurants():
        name = r["name"].lower()
        if q in name or name in q:
            matches.append(r)
    return matches


def find_restaurants_by_vibe(vibe: str) -> list[dict]:
    vibe_lower = vibe.lower().strip()
    matches = []
    for r in load_restaurants():
        vibes = [v.lower() for v in r.get("vibes", [])]
        blob = " ".join(
            [
                r.get("vibe", ""),
                r.get("description", ""),
                r.get("environment", ""),
                r.get("food_style", ""),
            ]
        ).lower()
        if any(vibe_lower in v for v in vibes) or vibe_lower in blob:
            matches.append(r)
    return matches


def find_review_by_restaurant_name(query: str) -> dict | None:
    q = query.lower().strip()
    for review in load_reviews():
        if q in review["restaurant_name"].lower():
            return review
    return None
