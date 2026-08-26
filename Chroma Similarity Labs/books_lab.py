"""
Lab 3 — Book similarity search + metadata filters (Chroma + MiniLM).
"""

from __future__ import annotations

from chroma_utils import create_collection

BOOKS = [
    {
        "id": "book_1",
        "title": "The Great Gatsby",
        "author": "F. Scott Fitzgerald",
        "genre": "Classic",
        "year": 1925,
        "rating": 4.1,
        "pages": 180,
        "description": "A tragic tale of wealth, love, and the American Dream in the Jazz Age",
        "themes": "wealth, corruption, American Dream, social class",
        "setting": "New York, 1920s",
    },
    {
        "id": "book_2",
        "title": "To Kill a Mockingbird",
        "author": "Harper Lee",
        "genre": "Classic",
        "year": 1960,
        "rating": 4.3,
        "pages": 376,
        "description": "A powerful story of racial injustice and moral growth in the American South",
        "themes": "racism, justice, moral courage, childhood innocence",
        "setting": "Alabama, 1930s",
    },
    {
        "id": "book_3",
        "title": "1984",
        "author": "George Orwell",
        "genre": "Dystopian",
        "year": 1949,
        "rating": 4.4,
        "pages": 328,
        "description": "A chilling vision of totalitarian control and surveillance society",
        "themes": "totalitarianism, surveillance, freedom, truth",
        "setting": "Oceania, dystopian future",
    },
    {
        "id": "book_4",
        "title": "Harry Potter and the Philosopher's Stone",
        "author": "J.K. Rowling",
        "genre": "Fantasy",
        "year": 1997,
        "rating": 4.5,
        "pages": 223,
        "description": "A young wizard discovers his magical heritage and begins his education at Hogwarts",
        "themes": "friendship, courage, good vs evil, coming of age",
        "setting": "England, magical world",
    },
    {
        "id": "book_5",
        "title": "The Lord of the Rings",
        "author": "J.R.R. Tolkien",
        "genre": "Fantasy",
        "year": 1954,
        "rating": 4.5,
        "pages": 1216,
        "description": "An epic fantasy quest to destroy a powerful ring and save Middle-earth",
        "themes": "heroism, friendship, good vs evil, power corruption",
        "setting": "Middle-earth, fantasy realm",
    },
    {
        "id": "book_6",
        "title": "The Hitchhiker's Guide to the Galaxy",
        "author": "Douglas Adams",
        "genre": "Science Fiction",
        "year": 1979,
        "rating": 4.2,
        "pages": 224,
        "description": "A humorous space adventure following Arthur Dent across the galaxy",
        "themes": "absurdity, technology, existence, humor",
        "setting": "Space, various planets",
    },
    {
        "id": "book_7",
        "title": "Dune",
        "author": "Frank Herbert",
        "genre": "Science Fiction",
        "year": 1965,
        "rating": 4.3,
        "pages": 688,
        "description": "A complex tale of politics, religion, and ecology on a desert planet",
        "themes": "power, ecology, religion, politics",
        "setting": "Arrakis, distant future",
    },
    {
        "id": "book_8",
        "title": "The Hunger Games",
        "author": "Suzanne Collins",
        "genre": "Dystopian",
        "year": 2008,
        "rating": 4.2,
        "pages": 374,
        "description": "A teenage girl fights for survival in a brutal televised competition",
        "themes": "survival, oppression, sacrifice, rebellion",
        "setting": "Panem, dystopian future",
    },
]


def _book_document(book: dict) -> str:
    document = f"{book['title']} by {book['author']}. {book['description']} "
    document += f"Themes: {book['themes']}. Setting: {book['setting']}. "
    document += f"Genre: {book['genre']} published in {book['year']}."
    return document


def main() -> None:
    try:
        collection = create_collection(
            "book_collection",
            description="A collection for storing book data",
        )
        print(f"Collection created: {collection.name}")

        collection.add(
            ids=[b["id"] for b in BOOKS],
            documents=[_book_document(b) for b in BOOKS],
            metadatas=[
                {
                    "title": b["title"],
                    "author": b["author"],
                    "genre": b["genre"],
                    "year": b["year"],
                    "rating": b["rating"],
                    "pages": b["pages"],
                }
                for b in BOOKS
            ],
        )

        all_items = collection.get()
        print(f"Documents in collection: {len(all_items['documents'])}")

        print("=== Book Similarity Search ===")
        print("\n1. Magical fantasy adventures:")
        results = collection.query(
            query_texts=["magical fantasy adventure with friendship and courage"],
            n_results=3,
        )
        for i, (doc_id, _, distance) in enumerate(
            zip(results["ids"][0], results["documents"][0], results["distances"][0])
        ):
            meta = results["metadatas"][0][i]
            print(
                f"  {i + 1}. {meta['title']} by {meta['author']} "
                f"- Distance: {distance:.4f}"
            )

        print("\n=== Metadata Filtering ===")
        print("\n2. Fantasy and Science Fiction:")
        results = collection.get(
            where={"genre": {"$in": ["Fantasy", "Science Fiction"]}}
        )
        for i, _ in enumerate(results["ids"]):
            meta = results["metadatas"][i]
            print(f"  - {meta['title']}: {meta['genre']} ({meta['rating']}*)")

        print("\n3. Highly rated (4.3+):")
        results = collection.get(where={"rating": {"$gte": 4.3}})
        for i, _ in enumerate(results["ids"]):
            meta = results["metadatas"][i]
            print(f"  - {meta['title']}: {meta['rating']}*")

        print("\n=== Combined Search ===")
        print("\n4. Highly rated dystopian themes:")
        results = collection.query(
            query_texts=["dystopian society control oppression future"],
            n_results=3,
            where={"rating": {"$gte": 4.0}},
        )
        for i, (_, _, distance) in enumerate(
            zip(results["ids"][0], results["documents"][0], results["distances"][0])
        ):
            meta = results["metadatas"][0][i]
            print(
                f"  {i + 1}. {meta['title']} ({meta['year']}) - {meta['rating']}* "
                f"(distance={distance:.4f})"
            )
    except Exception as error:
        print(f"Error: {error}")


if __name__ == "__main__":
    main()
