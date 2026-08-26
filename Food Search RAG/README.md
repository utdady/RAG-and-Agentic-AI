# Food Search RAG

Interactive food similarity search + filtered search + RAG chatbot over `FoodDataSet.json` (Chroma + MiniLM).

- Embeddings: `all-MiniLM-L6-v2` via Chroma
- Chat (RAG): Groq / Ollama via [`../shared/llm.py`](../shared/llm.py)

## Setup

```powershell
cd "Food Search RAG"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python download_data.py
```

Copy repo-root `env.example` → `.env` (preferred). Optional per-project `.env` overrides.

## Entry points

| Script | Purpose |
|--------|---------|
| `python search_cli.py` | Interactive similarity search + `history` |
| `python advanced_cli.py` | Cuisine / calorie / combined filters |
| `python rag_chat.py` | Retrieve → LLM answer (+ `compare`) |
| `python compare_systems.py` | Side-by-side timing of approaches |
| `python calorie_checker.py` | Budget filter practice |
| `python result_limiter.py` | Experiment with `n_results` |

## Layout

- `shared_food.py` — load/normalize JSON, Chroma collection, search/filter
- `data/FoodDataSet.json` — downloaded (gitignored)
- `reference/original-lab-notes.md` — Watsonx lab paste (cleaned)

## Notes

Chroma collection create uses the portable `embedding_function=` API (not the lab’s Chroma 1.x-only `configuration=` block).
