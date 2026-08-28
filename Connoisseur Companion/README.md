# Connoisseur Companion

Fused **IBM California Culinary** course Modules 1–4 into one Gradio app:

| Module | Role here |
|--------|-----------|
| **1** | Structured restaurant/review/recipe data in `data/` |
| **2** | Chroma RAG in `rag/` (optional index; keyword fallback) |
| **3** | Multi-agent recommendation workflow in `agents/` |
| **4** | FastMCP server + ReAct chat host |

LLM stack matches the rest of this repo: **Groq** when `GROQ_API_KEY` is set, else **Ollama** via `shared/llm.py`.

## Quick start

```bash
cd "Connoisseur Companion"
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:7876

## Optional: build vector index (Module 2)

First run downloads `sentence-transformers/all-MiniLM-L6-v2`:

```bash
python -m rag
```

Without an index, retrieval uses keyword search over JSON (still works).

## Tabs

1. **Chat (MCP + tools)** — ReAct loop over MCP tools: restaurant lookup, vibe search, reviews, knowledge search.
2. **Deep recommendations** — Full multi-agent pipeline: profile → RAG → parallel analysis → synthesis.
3. **About** — Architecture notes and cross-links.

## MCP server (standalone)

```bash
python mcp/server.py
```

Tools: `get_restaurant_info`, `recommend_by_vibe`, `get_review`, `search_knowledge_base`

## Data

Bundled from Module 1 lesson outputs:

- `California-Culinary-Map.txt`
- `structured_restaurant_data.json`
- `augmented_user_review.json`
- `augmented_food_recipe.json`

Schema normalization lives in `data_loader.py` (fixes Module 4 filename/field mismatches).

## Env

Uses repo-root `.env`. See `env.example`. Port override: `CONNOISSEUR_PORT=7876`.

## Related

- [`Module 1 Build a Structured Generative AI Application/`](../Module%201%20Build%20a%20Structured%20Generative%20AI%20Application/) — original notebooks
- [`Module 2 Design a Multimodal RAG System/`](../Module%202%20Design%20a%20Multimodal%20RAG%20System/)
- [`Module 3 Combine Agents into a Multi-Agent System/`](../Module%203%20Combine%20Agents%20into%20a%20Multi-Agent%20System/)
- [`Module 4 Integrate Agents, RAG, and Tools with MCP/`](../Module%204%20Integrate%20Agents,%20RAG,%20and%20Tools%20with%20MCP/)
- [`MCP Labs/`](../MCP%20Labs/) — general MCP curriculum

## Notes

Educational demo — not affiliated with IBM or restaurant listings. Watsonx/OpenAI/Anthropic from the course labs are replaced with Groq/Ollama.
