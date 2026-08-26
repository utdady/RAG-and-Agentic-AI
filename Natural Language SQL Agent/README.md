# Natural Language SQL Agent

Gradio (+ CLI) LangChain **SQL agent** over the **Chinook** sample database.

- **LLM:** Groq / Ollama via [`../shared/llm.py`](../shared/llm.py)
- **DB default:** local SQLite Chinook (downloaded on first run)
- **Not Watsonx + Skills Network MySQL** — course used Granite + ephemeral MySQL credentials (do not commit those)

## Setup

```powershell
cd "Natural Language SQL Agent"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Repo-root `.env` with `GROQ_API_KEY` (or Ollama).

## Run

```powershell
python app.py
```

Open http://127.0.0.1:7866

CLI (matches course `--prompt` style):

```powershell
python cli.py --prompt "How many Album are there in the database?"
```

### Optional MySQL

Set `DATABASE_URL` (and install `mysql-connector-python`). Leave unset to use local SQLite.

## Reference

[`reference/original-lab-notes.md`](reference/original-lab-notes.md)
