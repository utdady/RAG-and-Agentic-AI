"""Calorie budget checker over similarity search."""

from __future__ import annotations

from download_data import main as download_assets
from shared_food import (
    create_similarity_search_collection,
    load_food_data,
    perform_filtered_similarity_search,
    perform_similarity_search,
    populate_similarity_collection,
)

download_assets()


def calorie_checker() -> None:
    print("FOOD CALORIE BUDGET CHECKER")
    print("=" * 35)
    food_items = load_food_data()
    collection = create_similarity_search_collection("calorie_checker")
    populate_similarity_collection(collection, food_items)

    while True:
        try:
            budget = int(input("\nCalorie budget per meal? ").strip())
            if budget > 0:
                break
        except ValueError:
            pass
        print("Enter a positive number.")

    print(f"Budget: {budget} calories")
    while True:
        term = input("\nSearch food (or 'quit'): ").strip()
        if term.lower() == "quit":
            print("Goodbye!")
            break
        if not term:
            continue
        in_budget = perform_filtered_similarity_search(
            collection, term, max_calories=budget, n_results=5
        )
        all_hits = perform_similarity_search(collection, term, 5)
        print(f"\nResults for '{term}':")
        if in_budget:
            print(f"Within {budget} cal:")
            for i, r in enumerate(in_budget, 1):
                rem = budget - r["food_calories_per_serving"]
                print(
                    f"  {i}. {r['food_name']} — {r['food_calories_per_serving']} cal "
                    f"({rem} remaining) [{r['cuisine_type']}]"
                )
        else:
            print(f"No hits within {budget} calories.")

        over = [r for r in all_hits if r["food_calories_per_serving"] > budget]
        if over:
            print("Over budget (similar):")
            for i, r in enumerate(over[:3], 1):
                excess = r["food_calories_per_serving"] - budget
                print(
                    f"  {i}. {r['food_name']} — {r['food_calories_per_serving']} cal "
                    f"({excess} over)"
                )


if __name__ == "__main__":
    calorie_checker()
