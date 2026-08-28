# Original lab notes — Connoisseur Companion (Modules 1–4 fusion)

This project merges the IBM Skills Network **California Culinary / Connoisseur** track into one runnable app.

## Source modules

### Module 1 — Build a Structured Generative AI Application
- L1: Structure `California-Culinary-Map.txt` → JSON (Watsonx in course; data pre-generated in `data/`)
- L2: Multimodal review/recipe augmentation (vision captions)
- L3: CLI restaurant data management

**Integrated as:** `data/` + `data_loader.py` (schema normalization)

### Module 2 — Design a Multimodal RAG System
- L1: Chroma indexes for articles + recipe images (CLIP + MiniLM in course)
- L2: Metadata-filtered retrieval
- L3: Cross-modal score fusion

**Integrated as:** `rag/index.py`, `rag/retrieve.py` (text Chroma + keyword fallback; full CLIP/image index optional future work)

### Module 3 — Combine Agents into a Multi-Agent System
- L1: Six specialized agent personas
- L2: Hybrid workflow (profile → retrieve → parallel analysis → synthesize)
- L3: Gradio chatbot (course used mock workflow hook)

**Integrated as:** `agents/workflow.py` wired to real RAG retrieval

### Module 4 — Integrate Agents, RAG, and Tools with MCP
- L1: FastMCP server (restaurant tools + culinary map resource)
- L2: MCP client with sampling/roots (Anthropic in course)
- L3: Gradio MCP host (Watsonx ReAct in course)

**Integrated as:** `mcp/server.py` + Chat tab in `app.py` (Groq/Ollama via `shared/llm.py`)

## Pivot from course stack

| Course | This repo |
|--------|-----------|
| Watsonx | Groq / Ollama |
| OpenAI (M3) | Groq / Ollama |
| Anthropic client (M4 L2) | Not required for main app |
| Chroma in `~/chroma_multimodal` | `chroma_db/` under project |

## Schema fixes applied

- Module 4 expected `structured-restaurant-data.json` → uses M1 `structured_restaurant_data.json`
- M4 review fields (`restaurant_name`, `review_text`) joined from M1 reviews via `itemId`
- M4 vibe fields (`vibes[]`, `neighborhood`) mapped from M1 `vibe`, `location`

## Ports

- **7876** — Connoisseur Companion Gradio app (`CONNOISSEUR_PORT`)
