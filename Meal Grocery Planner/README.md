# Structured Meal & Grocery Planner

Gradio + **CrewAI** multi-agent meal planner with structured Pydantic outputs.

Pipeline: meal research (Serper) → shopping list → budget tips → leftovers → optional nutrition → summary report.

- **LLM:** Groq / Ollama via CrewAI `LLM`
- **Search:** Serper (`SERPER_API_KEY`)
- **Not Watsonx** — course used Granite on watsonx
- Related curriculum: [`../CrewAI Labs/`](../CrewAI%20Labs/) (research/writer crew)

## Setup

```powershell
cd "Meal Grocery Planner"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Repo-root `.env`: `GROQ_API_KEY` + `SERPER_API_KEY`.

## Run

```powershell
python app.py
```

Open http://127.0.0.1:7868

Outputs (JSON/MD) land in `outputs/` (gitignored).

Educational only — not medical or dietary advice.

## Reference

[`reference/original-lab-notes.md`](reference/original-lab-notes.md)
