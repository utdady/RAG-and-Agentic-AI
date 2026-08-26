"""Advanced food search with cuisine / calorie filters."""

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

CUISINES = [
    "Italian",
    "Thai",
    "Mexican",
    "Indian",
    "Japanese",
    "French",
    "Mediterranean",
    "American",
    "Health Food",
    "Dessert",
]


def display_search_results(results, title: str, show_details: bool = True) -> None:
    print(f"\n{title}")
    print("=" * 50)
    if not results:
        print("No matching results.")
        return
    for i, result in enumerate(results, 1):
        pct = result["similarity_score"] * 100
        if show_details:
            print(f"\n{i}. {result['food_name']}")
            print(f"   Similarity: {pct:.1f}%")
            print(f"   Cuisine: {result['cuisine_type']}")
            print(f"   Calories: {result['food_calories_per_serving']}")
            print(f"   {result['food_description']}")
        else:
            print(f"   {i}. {result['food_name']} ({pct:.1f}% match)")
    print("=" * 50)


def perform_basic_search(collection) -> None:
    query = input("Enter search query: ").strip()
    if not query:
        print("Please enter a search term")
        return
    results = perform_similarity_search(collection, query, 5)
    display_search_results(results, "Basic Search Results")


def perform_cuisine_filtered_search(collection) -> None:
    print("Available cuisines:")
    for i, cuisine in enumerate(CUISINES, 1):
        print(f"  {i}. {cuisine}")
    query = input("\nEnter search query: ").strip()
    cuisine_choice = input("Enter cuisine number (or name): ").strip()
    if not query:
        print("Please enter a search term")
        return
    cuisine_filter = None
    if cuisine_choice.isdigit():
        idx = int(cuisine_choice) - 1
        if 0 <= idx < len(CUISINES):
            cuisine_filter = CUISINES[idx]
    else:
        cuisine_filter = cuisine_choice or None
    if not cuisine_filter:
        print("Invalid cuisine selection")
        return
    results = perform_filtered_similarity_search(
        collection, query, cuisine_filter=cuisine_filter, n_results=5
    )
    display_search_results(results, f"Cuisine-Filtered ({cuisine_filter})")


def perform_calorie_filtered_search(collection) -> None:
    query = input("Enter search query: ").strip()
    max_cal_in = input("Max calories (Enter = no limit): ").strip()
    if not query:
        print("Please enter a search term")
        return
    max_calories = int(max_cal_in) if max_cal_in.isdigit() else None
    results = perform_filtered_similarity_search(
        collection, query, max_calories=max_calories, n_results=5
    )
    label = f"under {max_calories} cal" if max_calories else "any calories"
    display_search_results(results, f"Calorie-Filtered ({label})")


def perform_combined_filtered_search(collection) -> None:
    query = input("Enter search query: ").strip()
    cuisine = input("Cuisine type (optional): ").strip() or None
    max_cal_in = input("Max calories (optional): ").strip()
    if not query:
        print("Please enter a search term")
        return
    max_calories = int(max_cal_in) if max_cal_in.isdigit() else None
    parts = []
    if cuisine:
        parts.append(f"cuisine: {cuisine}")
    if max_calories:
        parts.append(f"max cal: {max_calories}")
    filter_text = ", ".join(parts) if parts else "no filters"
    results = perform_filtered_similarity_search(
        collection,
        query,
        cuisine_filter=cuisine,
        max_calories=max_calories,
        n_results=5,
    )
    display_search_results(results, f"Combined ({filter_text})")


def run_search_demonstrations(collection) -> None:
    demos = [
        {"title": "Italian Cuisine", "query": "creamy pasta", "cuisine": "Italian", "cal": None},
        {"title": "Low-Calorie Healthy", "query": "healthy meal", "cuisine": None, "cal": 300},
        {"title": "Asian Light", "query": "light fresh meal", "cuisine": "Japanese", "cal": 250},
    ]
    for demo in demos:
        print(f"\nDemo: {demo['title']} | query='{demo['query']}'")
        results = perform_filtered_similarity_search(
            collection,
            demo["query"],
            cuisine_filter=demo["cuisine"],
            max_calories=demo["cal"],
            n_results=3,
        )
        display_search_results(results, demo["title"], show_details=False)
        input("Press Enter for next demo...")


def show_advanced_help() -> None:
    print("\nADVANCED SEARCH HELP")
    print("1 Basic | 2 Cuisine | 3 Calories | 4 Combined | 5 Demos | 6 Help | 7 Exit")
    print("Tips: 'creamy', 'spicy', cuisine names, calorie caps.")


def interactive_advanced_search(collection) -> None:
    print("\n" + "=" * 50)
    print("ADVANCED SEARCH WITH FILTERS")
    print("=" * 50)
    print("1 Basic  2 Cuisine  3 Calories  4 Combined  5 Demos  6 Help  7 Exit")
    while True:
        try:
            choice = input("\nSelect (1-7): ").strip()
            if choice == "1":
                perform_basic_search(collection)
            elif choice == "2":
                perform_cuisine_filtered_search(collection)
            elif choice == "3":
                perform_calorie_filtered_search(collection)
            elif choice == "4":
                perform_combined_filtered_search(collection)
            elif choice == "5":
                run_search_demonstrations(collection)
            elif choice == "6":
                show_advanced_help()
            elif choice == "7":
                print("Goodbye!")
                break
            else:
                print("Invalid option.")
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


def main() -> None:
    print("Advanced Food Search System")
    food_items = load_food_data()
    if not food_items:
        raise SystemExit("No food data loaded.")
    collection = create_similarity_search_collection(
        "advanced_food_search",
        {"description": "advanced food search"},
    )
    populate_similarity_collection(collection, food_items)
    interactive_advanced_search(collection)


if __name__ == "__main__":
    main()
