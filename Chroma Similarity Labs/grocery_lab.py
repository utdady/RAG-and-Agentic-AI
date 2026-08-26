"""
Lab 1 — Similarity search on plain grocery text (Chroma + MiniLM).
"""

from __future__ import annotations

from chroma_utils import create_collection, print_query_hits


TEXTS = [
    "fresh red apples",
    "organic bananas",
    "ripe mangoes",
    "whole wheat bread",
    "farm-fresh eggs",
    "natural yogurt",
    "frozen vegetables",
    "grass-fed beef",
    "free-range chicken",
    "fresh salmon fillet",
    "aromatic coffee beans",
    "pure honey",
    "golden apple",
    "red fruit",
]


def main() -> None:
    try:
        collection = create_collection(
            "my_grocery_collection",
            description="A collection for storing grocery data",
        )
        print(f"Collection created: {collection.name}")

        ids = [f"food_{i + 1}" for i in range(len(TEXTS))]
        collection.add(
            documents=TEXTS,
            metadatas=[
                {"source": "grocery_store", "category": "food"} for _ in TEXTS
            ],
            ids=ids,
        )

        all_items = collection.get()
        print(f"Documents in collection: {len(all_items['documents'])}")

        print("\n=== Single query: apple ===")
        results = collection.query(query_texts=["apple"], n_results=3)
        print_query_hits(results, "apple")

        print("\n=== Batch queries: red, fresh ===")
        queries = ["red", "fresh"]
        batch = collection.query(query_texts=queries, n_results=3)
        for q_idx, q in enumerate(queries):
            print(f'\nTop 3 for "{q}":')
            if not batch["ids"][q_idx]:
                print("  (none)")
                continue
            for i in range(min(3, len(batch["ids"][q_idx]))):
                print(
                    f"  - {batch['ids'][q_idx][i]}: "
                    f"\"{batch['documents'][q_idx][i]}\" "
                    f"(distance={batch['distances'][q_idx][i]:.4f})"
                )
    except Exception as error:
        print(f"Error: {error}")


if __name__ == "__main__":
    main()
