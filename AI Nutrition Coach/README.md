# AI Nutrition Coach

Flask app: upload a meal photo → vision LLM calorie / nutrient breakdown.

- **LLM:** Groq vision or Ollama LLaVA (repo-root `.env`)
- **Not Watsonx** — course used Llama multimodal chat on watsonx.ai

## Setup

```powershell
cd "AI Nutrition Coach"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Ensure `GROQ_API_KEY` (or Ollama + `llava`) in repo-root `.env`.

## Run

```powershell
python app.py
```

Open http://127.0.0.1:5002

Estimates are approximate — the UI includes the course medical disclaimer.

## Reference

[`reference/original-lab-notes.md`](reference/original-lab-notes.md)
