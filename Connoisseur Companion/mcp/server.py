"""
Connoisseur MCP server (Module 4) — tools over Module 1 data + Module 2 RAG.

Run: python mcp/server.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from fastmcp import FastMCP

HERE = Path(__file__).resolve().parent.parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from data_loader import (
    find_restaurants_by_name,
    find_restaurants_by_vibe,
    find_review_by_restaurant_name,
    load_culinary_map,
)
from rag.retrieve import search_knowledge

mcp = FastMCP("Connoisseur-Server")


@mcp.resource("culinary-map://california")
def get_culinary_map() -> str:
    """Full raw California Culinary Map text from Module 1."""
    return load_culinary_map()


@mcp.tool()
def get_restaurant_info(restaurant_name: str) -> str:
    """Search restaurants by name; returns structured details (cuisine, rating, vibe, signatures)."""
    matches = find_restaurants_by_name(restaurant_name)
    if not matches:
        return json.dumps(
            {
                "status": "not_found",
                "message": f"No restaurant found matching '{restaurant_name}'.",
                "suggestion": "Try a partial name like 'Iron' or 'Sakura'.",
            },
            indent=2,
        )
    return json.dumps({"status": "found", "count": len(matches), "results": matches}, indent=2)


@mcp.tool()
def recommend_by_vibe(vibe: str) -> str:
    """Find restaurants matching a vibe/atmosphere keyword (e.g. moody, romantic, sun-drenched)."""
    structured = find_restaurants_by_vibe(vibe)
    vibe_lower = vibe.lower().strip()
    excerpts = []
    for para in load_culinary_map().split("\n\n"):
        if vibe_lower in para.lower() and para.strip():
            excerpts.append(para.strip()[:300])

    slim = [
        {
            "name": r["name"],
            "neighborhood": r["location"],
            "cuisine": r["cuisine"],
            "rating": r["rating"],
            "vibes": r["vibes"],
            "price_range": r["price_range"],
        }
        for r in structured
    ]
    return json.dumps(
        {
            "vibe_searched": vibe,
            "structured_matches": slim,
            "raw_text_excerpts": excerpts[:5],
        },
        indent=2,
    )


@mcp.tool()
def get_review(restaurant_name: str) -> str:
    """Retrieve user review text and rating for a restaurant."""
    review = find_review_by_restaurant_name(restaurant_name)
    if not review:
        return json.dumps(
            {
                "status": "not_found",
                "message": f"No review found for '{restaurant_name}'.",
            },
            indent=2,
        )
    return json.dumps({"status": "found", **review}, indent=2)


@mcp.tool()
def search_knowledge_base(query: str, location: str = "") -> str:
    """Semantic/keyword search over restaurants and recipes (Module 2 RAG layer)."""
    loc = location.strip() or None
    result = search_knowledge(query, k=8, location=loc)
    return json.dumps(result, indent=2)


if __name__ == "__main__":
    mcp.run()
