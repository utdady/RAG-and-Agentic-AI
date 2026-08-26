# Data Viz Agent

Gradio chat over LangChain’s **pandas dataframe agent** on the course `student-mat` dataset. Ask for stats or charts; generated matplotlib figures appear in the gallery.

- **LLM:** Groq / Ollama via [`../shared/llm.py`](../shared/llm.py)
- **Not Watsonx** — course used Llama 4 Maverick on watsonx.ai
- Related (different tools): [`../AI Powered Data Analysis/`](../AI%20Powered%20Data%20Analysis/) (CSV inspect + sklearn, no plotting agent)

## Setup

```powershell
cd "Data Viz Agent"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Ensure `GROQ_API_KEY` (or Ollama) in repo-root `.env`.

## Run

```powershell
python app.py
```

Open http://127.0.0.1:7865

Dataset downloads to `data/student-mat.csv` on first run.

## Security

Uses `allow_dangerous_code=True` so the model can **execute Python** against the dataframe. Intended for local demos only — do not expose publicly without a sandbox.

## Reference

[`reference/original-lab-notes.md`](reference/original-lab-notes.md)
