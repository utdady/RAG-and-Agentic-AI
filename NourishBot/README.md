# AI NourishBot

Gradio + **CrewAI** multimodal nutrition coach.

| Workflow | Pipeline |
|----------|----------|
| **recipe** | Vision extract ingredients → dietary filter → recipe ideas (Pydantic) |
| **analysis** | Vision nutrient / calorie report (Pydantic) |

- **Vision:** Groq (`GROQ_VISION_MODEL`) or Ollama LLaVA
- **Agents:** Groq / Ollama via CrewAI `LLM`
- **Not Watsonx** — course used Llama multimodal + Granite on watsonx.ai
- Related: simpler single-call Flask app in [`../AI Nutrition Coach/`](../AI%20Nutrition%20Coach/); meal text planning in [`../Meal Grocery Planner/`](../Meal%20Grocery%20Planner/)

## Setup

```powershell
cd NourishBot
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Repo-root `.env`: `GROQ_API_KEY` (and optional `GROQ_VISION_MODEL`). For Ollama, pull a vision model (`ollama pull llava`) and set `LLM_PROVIDER=ollama`.

## Run

```powershell
python app.py
```

Open http://127.0.0.1:7869

Example fridge/dish images download automatically into `examples/` on first launch (IBM Skills Network sample URLs).

Educational estimates only — not medical advice.

## Reference

[`reference/original-lab-notes.md`](reference/original-lab-notes.md)
