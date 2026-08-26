"""RAG food recommendation chatbot (Groq / Ollama via shared.llm)."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

HERE = Path(__file__).resolve().parent

from shared.env_load import load_env
from shared.llm import describe_setup, get_llm_info

load_env(HERE)
from download_data import main as download_assets
from shared_food import (
    create_similarity_search_collection,
    load_food_data,
    perform_similarity_search,
    populate_similarity_collection,
)

download_assets()

llm, llm_info = get_llm_info(temperature=0.4)
print(describe_setup())
print(f"Chat LLM={llm_info.provider}:{llm_info.model}")


def _llm_text(prompt: str) -> str:
    resp = llm.invoke(prompt)
    return getattr(resp, "content", str(resp)).strip()


def prepare_context_for_llm(query: str, search_results: list[dict]) -> str:
    if not search_results:
        return "No relevant food items found in the database."
    parts = [
        "Based on your query, here are the most relevant food options:",
        "",
    ]
    for i, result in enumerate(search_results[:3], 1):
        parts.append(f"Option {i}: {result['food_name']}")
        parts.append(f"  - Description: {result['food_description']}")
        parts.append(f"  - Cuisine: {result['cuisine_type']}")
        parts.append(f"  - Calories: {result['food_calories_per_serving']} per serving")
        ing = result.get("food_ingredients")
        if ing:
            parts.append(f"  - Key ingredients: {ing}")
        if result.get("food_health_benefits"):
            parts.append(f"  - Health benefits: {result['food_health_benefits']}")
        if result.get("cooking_method"):
            parts.append(f"  - Cooking method: {result['cooking_method']}")
        if result.get("taste_profile"):
            parts.append(f"  - Taste profile: {result['taste_profile']}")
        parts.append(f"  - Similarity score: {result['similarity_score'] * 100:.1f}%")
        parts.append("")
    return "\n".join(parts)


def generate_fallback_response(query: str, search_results: list[dict]) -> str:
    if not search_results:
        return (
            "I couldn't find matching foods. Try different words for what "
            "you're in the mood for."
        )
    top = search_results[0]
    text = (
        f"Based on '{query}', I'd recommend {top['food_name']}. "
        f"It's {top['cuisine_type']} cuisine at "
        f"{top['food_calories_per_serving']} calories per serving."
    )
    if len(search_results) > 1:
        text += f" Another option: {search_results[1]['food_name']}."
    return text


def generate_llm_rag_response(query: str, search_results: list[dict]) -> str:
    context = prepare_context_for_llm(query, search_results)
    prompt = f"""You are a helpful food recommendation assistant.

User Query: "{query}"

Retrieved Food Information:
{context}

Write a short response that:
1. Acknowledges the request
2. Recommends 2-3 items from the retrieved options
3. Explains why they fit
4. Mentions cuisine/calories/benefits when useful
5. Stays friendly and concise

Response:"""
    try:
        text = _llm_text(prompt)
        if len(text) < 40:
            return generate_fallback_response(query, search_results)
        return text
    except Exception as e:
        print(f"LLM error: {e}")
        return generate_fallback_response(query, search_results)


def generate_simple_comparison(q1, q2, r1, r2) -> str:
    if not r1 and not r2:
        return "No results for either query."
    if not r1:
        return f"Found results for '{q2}' but none for '{q1}'."
    if not r2:
        return f"Found results for '{q1}' but none for '{q2}'."
    return (
        f"For '{q1}', try {r1[0]['food_name']}. "
        f"For '{q2}', try {r2[0]['food_name']}."
    )


def generate_llm_comparison(q1, q2, r1, r2) -> str:
    try:
        prompt = f"""Compare these two food preference queries briefly.

Query 1: "{q1}"
{prepare_context_for_llm(q1, r1[:3])}

Query 2: "{q2}"
{prepare_context_for_llm(q2, r2[:3])}

Cover: key differences, overlaps, best pick from each. Keep it short.

Comparison:"""
        text = _llm_text(prompt)
        return text if len(text) >= 40 else generate_simple_comparison(q1, q2, r1, r2)
    except Exception:
        return generate_simple_comparison(q1, q2, r1, r2)


def handle_enhanced_rag_query(collection, query: str) -> None:
    print(f"\nSearching for: '{query}'...")
    results = perform_similarity_search(collection, query, 3)
    if not results:
        print("No matching foods found.")
        return
    print(f"Found {len(results)} matches — generating answer...")
    print(f"\nBot: {generate_llm_rag_response(query, results)}")
    print("\nSearch details:")
    for i, r in enumerate(results[:3], 1):
        print(
            f"  {i}. {r['food_name']} | {r['cuisine_type']} | "
            f"{r['food_calories_per_serving']} cal | "
            f"{r['similarity_score'] * 100:.1f}% match"
        )


def handle_enhanced_comparison_mode(collection) -> None:
    print("\nCOMPARISON MODE")
    q1 = input("First query: ").strip()
    q2 = input("Second query: ").strip()
    if not q1 or not q2:
        print("Need both queries.")
        return
    r1 = perform_similarity_search(collection, q1, 3)
    r2 = perform_similarity_search(collection, q2, 3)
    print(f"\nAI analysis: {generate_llm_comparison(q1, q2, r1, r2)}")
    print("\nSide-by-side top hits:")
    for i in range(3):
        left = (
            f"{r1[i]['food_name']} ({r1[i]['similarity_score'] * 100:.0f}%)"
            if i < len(r1)
            else "---"
        )
        right = (
            f"{r2[i]['food_name']} ({r2[i]['similarity_score'] * 100:.0f}%)"
            if i < len(r2)
            else "---"
        )
        print(f"  {left:32} | {right}")


def show_help() -> None:
    print("\nRAG FOOD CHAT HELP")
    print("Ask in natural language, e.g. 'spicy healthy dinner under 400 calories'")
    print("Commands: compare | help | quit")


def enhanced_rag_food_chatbot(collection) -> None:
    print("\n" + "=" * 60)
    print("RAG FOOD RECOMMENDATION CHATBOT")
    print(f"  LLM: {llm_info.provider}:{llm_info.model}")
    print("=" * 60)
    print("Commands: help | compare | quit")
    while True:
        try:
            user_input = input("\nYou: ").strip()
            if not user_input:
                continue
            low = user_input.lower()
            if low in {"quit", "exit", "q"}:
                print("Goodbye!")
                break
            if low in {"help", "h"}:
                show_help()
            elif low == "compare":
                handle_enhanced_comparison_mode(collection)
            else:
                handle_enhanced_rag_query(collection, user_input)
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


def main() -> None:
    print("Enhanced RAG Food Recommendation Chatbot")
    food_items = load_food_data()
    if not food_items:
        raise SystemExit("No food data loaded.")
    collection = create_similarity_search_collection(
        "enhanced_rag_food_chatbot",
        {"description": "RAG food chatbot"},
    )
    populate_similarity_collection(collection, food_items)
    enhanced_rag_food_chatbot(collection)


if __name__ == "__main__":
    main()
