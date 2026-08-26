"""Interactive food similarity search CLI (with search history)."""

from __future__ import annotations

from download_data import main as download_assets
from shared_food import (
    create_similarity_search_collection,
    load_food_data,
    perform_similarity_search,
    populate_similarity_collection,
)

download_assets()

search_history: list[str] = []


def show_help_menu() -> None:
    print("\nHELP")
    print("-" * 30)
    print("Examples: 'chocolate dessert', 'Italian food', 'sweet treats'")
    print("Commands: help | history | quit")


def handle_history_command() -> None:
    if not search_history:
        print("No search history yet.")
        return
    print("\nSearch history (last 10):")
    for i, search in enumerate(search_history[-10:], 1):
        print(f"  {i}. {search}")


def suggest_related_searches(results: list[dict]) -> None:
    if not results:
        return
    cuisines = list({r["cuisine_type"] for r in results})
    print("\nRelated ideas:")
    for cuisine in cuisines[:3]:
        print(f"  • '{cuisine} dishes'")
    avg_cal = sum(r["food_calories_per_serving"] for r in results) / len(results)
    if avg_cal > 350:
        print("  • 'low calorie' for lighter options")
    else:
        print("  • 'hearty meal' for more substantial dishes")


def handle_food_search(collection, query: str) -> None:
    search_history.append(query)
    print(f"\nSearching for '{query}'...")
    results = perform_similarity_search(collection, query, 5)
    if not results:
        print("No matches. Try cuisine, ingredient, or taste keywords.")
        return

    print(f"\nFound {len(results)} recommendations:")
    print("=" * 60)
    for i, result in enumerate(results, 1):
        pct = result["similarity_score"] * 100
        print(f"\n{i}. {result['food_name']}")
        print(f"   Match: {pct:.1f}%")
        print(f"   Cuisine: {result['cuisine_type']}")
        print(f"   Calories: {result['food_calories_per_serving']} / serving")
        print(f"   {result['food_description']}")
        if i < len(results):
            print("   " + "-" * 50)
    print("=" * 60)
    suggest_related_searches(results)


def interactive_food_chatbot(collection) -> None:
    print("\n" + "=" * 50)
    print("INTERACTIVE FOOD SEARCH")
    print("=" * 50)
    print("Type a query, or: help | history | quit")
    print("-" * 50)

    while True:
        try:
            user_input = input("\nSearch for food: ").strip()
            if not user_input:
                continue
            low = user_input.lower()
            if low in {"quit", "exit", "q"}:
                print("Goodbye!")
                break
            if low in {"help", "h"}:
                show_help_menu()
            elif low == "history":
                handle_history_command()
            else:
                handle_food_search(collection, user_input)
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


def main() -> None:
    print("Interactive Food Recommendation System")
    print("=" * 50)
    food_items = load_food_data()
    if not food_items:
        raise SystemExit("No food data loaded.")
    collection = create_similarity_search_collection(
        "interactive_food_search",
        {"description": "interactive food search"},
    )
    populate_similarity_collection(collection, food_items)
    interactive_food_chatbot(collection)


if __name__ == "__main__":
    main()
