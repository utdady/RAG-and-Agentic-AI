"""Compare interactive / advanced / RAG-style responses on one query."""

from __future__ import annotations

import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

HERE = Path(__file__).resolve().parent
load_dotenv(HERE / ".env")
load_dotenv(ROOT / ".env")
load_dotenv(ROOT / "Meeting Assistant" / ".env")

from download_data import main as download_assets
from shared_food import (
    create_similarity_search_collection,
    load_food_data,
    perform_filtered_similarity_search,
    perform_similarity_search,
    populate_similarity_collection,
)

download_assets()


def main() -> None:
    print("FOOD SEARCH SYSTEMS COMPARISON")
    print("=" * 50)
    food_items = load_food_data()
    if not food_items:
        raise SystemExit("No food data loaded.")

    interactive = create_similarity_search_collection("comparison_interactive")
    advanced = create_similarity_search_collection("comparison_advanced")
    rag = create_similarity_search_collection("comparison_rag")
    for coll in (interactive, advanced, rag):
        populate_similarity_collection(coll, food_items)

    test_query = "chocolate dessert"
    print(f"\nTest query: '{test_query}'")

    print("\n1) INTERACTIVE SEARCH")
    t0 = time.time()
    interactive_results = perform_similarity_search(interactive, test_query, 3)
    interactive_time = time.time() - t0
    for i, r in enumerate(interactive_results, 1):
        print(f"  {i}. {r['food_name']} ({r['similarity_score'] * 100:.1f}%)")
        print(f"     {r['food_description']}")
    print(f"  Time: {interactive_time:.3f}s")

    print("\n2) ADVANCED SEARCH (basic + Indian filter)")
    t0 = time.time()
    basic = perform_similarity_search(advanced, test_query, 3)
    print("  Basic:")
    for i, r in enumerate(basic, 1):
        print(
            f"    {i}. {r['food_name']} — {r['cuisine_type']} "
            f"({r['food_calories_per_serving']} cal)"
        )
    filtered = perform_filtered_similarity_search(
        advanced, test_query, cuisine_filter="Indian", n_results=2
    )
    print("  Filtered Indian:")
    for i, r in enumerate(filtered, 1):
        print(f"    {i}. {r['food_name']} ({r['similarity_score'] * 100:.1f}%)")
    advanced_time = time.time() - t0
    print(f"  Time: {advanced_time:.3f}s")

    print("\n3) RAG-STYLE (retrieve + LLM if available)")
    t0 = time.time()
    rag_results = perform_similarity_search(rag, test_query, 3)
    try:
        from shared.llm import get_chat_llm

        llm = get_chat_llm(temperature=0.3)
        ctx = "\n".join(
            f"- {r['food_name']}: {r['food_description']} "
            f"({r['food_calories_per_serving']} cal)"
            for r in rag_results
        )
        prompt = (
            f"User wants: {test_query}\nCandidates:\n{ctx}\n"
            "Recommend 1-2 options in 2 short sentences."
        )
        resp = llm.invoke(prompt)
        text = getattr(resp, "content", str(resp)).strip()
        print(f"  Bot: {text}")
    except Exception as e:
        if rag_results:
            top, second = rag_results[0], rag_results[1] if len(rag_results) > 1 else None
            text = (
                f"I'd recommend {top['food_name']} "
                f"({top['similarity_score'] * 100:.0f}% match, "
                f"{top['food_calories_per_serving']} cal)."
            )
            if second:
                text += f" Also consider {second['food_name']}."
            print(f"  Bot (fallback): {text}")
            print(f"  (LLM skipped: {e})")
        else:
            print("  No results.")
    rag_time = time.time() - t0
    print(f"  Time: {rag_time:.3f}s")

    print("\nSUMMARY")
    print("  Interactive: fast ranked list")
    print("  Advanced: filters for cuisine / calories")
    print("  RAG: natural-language explanation over retrieved hits")
    print(
        f"  Times — interactive {interactive_time:.3f}s | "
        f"advanced {advanced_time:.3f}s | rag {rag_time:.3f}s"
    )


if __name__ == "__main__":
    main()
