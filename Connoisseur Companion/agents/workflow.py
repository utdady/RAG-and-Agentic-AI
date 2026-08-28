"""Multi-agent recommendation workflow (Module 3) with real RAG retrieval."""

from __future__ import annotations

import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent.parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))
if str(HERE.parent) not in sys.path:
    sys.path.insert(0, str(HERE.parent))

from langchain_core.messages import HumanMessage, SystemMessage

from rag.retrieve import search_knowledge
from shared.llm import get_chat_llm

AGENT_PROMPTS = {
    "profile": (
        "You are a User Profile Generator. Extract structured dining preferences from the user message. "
        "Return ONLY valid JSON with keys: cuisines (list), vibes (list), location (string or null), "
        "price_preference (string), dietary_notes (list), summary (string)."
    ),
    "trends": (
        "You are a Food Trend Analyst. Given candidates and a user profile, identify 3-5 relevant trends. "
        "Return ONLY valid JSON: {\"trends\": [{\"name\": str, \"relevance\": str}]}"
    ),
    "styles": (
        "You are a Food Style Expert. Analyze cuisine and flavor alignment with the user profile. "
        "Return ONLY valid JSON: {\"style_notes\": str, \"best_matches\": [str]}"
    ),
    "nutrition": (
        "You are a Nutrition Expert. Flag dietary concerns and lighter options. "
        "Return ONLY valid JSON: {\"notes\": str, \"warnings\": [str], \"lighter_picks\": [str]}"
    ),
    "recommend": (
        "You are a Recommendation Expert. Synthesize profile, candidates, trend/style/nutrition analysis "
        "into final picks. Return ONLY valid JSON: "
        "{\"restaurants\": [{\"name\", \"location\", \"cuisine\", \"rating\", \"reason\"}], "
        "\"recipes\": [{\"name\", \"cuisine\", \"reason\"}]}"
    ),
}


def _call_llm(system: str, user: str, temperature: float = 0.4) -> str:
    llm = get_chat_llm(temperature=temperature)
    resp = llm.invoke(
        [SystemMessage(content=system), HumanMessage(content=user)]
    )
    content = resp.content
    if isinstance(content, list):
        return " ".join(
            b.get("text", "") if isinstance(b, dict) else str(b) for b in content
        )
    return str(content)


def _parse_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1] if lines[-1].startswith("```") else lines[1:])
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            return json.loads(text[start : end + 1])
        raise


def generate_profile(user_input: str) -> dict:
    raw = _call_llm(AGENT_PROMPTS["profile"], user_input)
    return _parse_json(raw)


def retrieve_candidates(profile: dict, k: int = 10) -> dict:
    query_parts = []
    if profile.get("cuisines"):
        query_parts.extend(profile["cuisines"])
    if profile.get("vibes"):
        query_parts.extend(profile["vibes"])
    if profile.get("summary"):
        query_parts.append(profile["summary"])
    query = " ".join(query_parts) or "California dining recommendations"
    location = profile.get("location") or None
    return search_knowledge(query, k=k, location=location)


def _analyze(agent_key: str, payload: dict) -> dict:
    raw = _call_llm(AGENT_PROMPTS[agent_key], json.dumps(payload, indent=2))
    return _parse_json(raw)


def run_recommendation_workflow(user_input: str) -> dict:
    """
    Hybrid workflow (Module 3 L2):
      Phase 1 — profile
      Phase 2 — RAG retrieval (Module 2)
      Phase 3 — parallel trend / style / nutrition analysis
      Phase 4 — synthesis
    """
    profile = generate_profile(user_input)
    candidates = retrieve_candidates(profile)

    analysis_payload = {
        "profile": profile,
        "retrieved_restaurants": candidates.get("restaurants", [])[:10],
        "retrieved_recipes": candidates.get("recipes", [])[:10],
    }

    with ThreadPoolExecutor(max_workers=3) as pool:
        fut_trends = pool.submit(_analyze, "trends", analysis_payload)
        fut_styles = pool.submit(_analyze, "styles", analysis_payload)
        fut_nutrition = pool.submit(_analyze, "nutrition", analysis_payload)
        trends = fut_trends.result()
        styles = fut_styles.result()
        nutrition = fut_nutrition.result()

    synthesis_payload = {
        **analysis_payload,
        "trends": trends,
        "styles": styles,
        "nutrition": nutrition,
    }
    recommendations = _parse_json(
        _call_llm(AGENT_PROMPTS["recommend"], json.dumps(synthesis_payload, indent=2))
    )

    return {
        "profile": profile,
        "candidates": candidates,
        "analysis": {"trends": trends, "styles": styles, "nutrition": nutrition},
        "recommendations": recommendations,
    }


def format_recommendations(result: dict) -> str:
    recs = result.get("recommendations") or {}
    lines = ["## Recommendations\n"]

    for r in recs.get("restaurants") or []:
        lines.append(
            f"**{r.get('name', 'Restaurant')}** ({r.get('location', 'CA')}) — "
            f"{r.get('cuisine', 'N/A')}. {r.get('reason', '')}"
        )

    if recs.get("recipes"):
        lines.append("\n### Recipes\n")
        for r in recs["recipes"]:
            lines.append(f"- **{r.get('name')}** ({r.get('cuisine')}): {r.get('reason', '')}")

    profile = result.get("profile") or {}
    if profile.get("summary"):
        lines.insert(1, f"_Profile: {profile['summary']}_\n")

    return "\n".join(lines)
