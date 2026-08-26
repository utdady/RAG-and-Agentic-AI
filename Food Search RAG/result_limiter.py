"""Experiment with different n_results limits."""

from __future__ import annotations

from download_data import main as download_assets
from shared_food import (
    create_similarity_search_collection,
    load_food_data,
    perform_similarity_search,
    populate_similarity_collection,
)

download_assets()


def test_result_limits() -> None:
    print("SIMILARITY SEARCH RESULT LIMITER")
    print("=" * 45)
    food_items = load_food_data()
    collection = create_similarity_search_collection("result_test")
    populate_similarity_collection(collection, food_items)

    query = "spicy chicken"
    print(f"Query: '{query}'\n")
    for limit in (1, 3, 5, 10):
        print(f"Top {limit}:")
        results = perform_similarity_search(collection, query, limit)
        for i, r in enumerate(results, 1):
            print(
                f"  {i}. {r['food_name']} score={r['similarity_score']:.3f} "
                f"({r['cuisine_type']}, {r['food_calories_per_serving']} cal)"
            )
        if results:
            scores = [r["similarity_score"] for r in results]
            print(
                f"  avg={sum(scores) / len(scores):.3f} "
                f"best={max(scores):.3f} worst={min(scores):.3f}"
            )
        print("-" * 45)

    print("\nInteractive mode (empty query exits)")
    while True:
        user_query = input("\nQuery: ").strip()
        if not user_query:
            break
        raw = input("How many results (1-20)? ").strip()
        limit = int(raw) if raw.isdigit() and 1 <= int(raw) <= 20 else 5
        results = perform_similarity_search(collection, user_query, limit)
        for i, r in enumerate(results, 1):
            print(f"  {i}. {r['food_name']} ({r['similarity_score']:.3f})")


if __name__ == "__main__":
    test_result_limits()
