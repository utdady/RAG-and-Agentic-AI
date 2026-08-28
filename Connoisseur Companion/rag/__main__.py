from rag.index import build_indexes

if __name__ == "__main__":
    path = build_indexes(force=False)
    print(f"Indexes ready at {path}")
