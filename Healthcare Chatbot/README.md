# Healthcare Chatbot

Gradio + **AutoGen (AG2)** multi-agent demos for educational healthcare scenarios.

| Tab | Agents |
|-----|--------|
| **Symptom consultation** | diagnosis → pharmacy → consultation (`round_robin`) |
| **Mental health support** | emotion analysis → self-care tips (`round_robin`) |

- **LLM:** Groq (`api_type: groq`) or Ollama OpenAI-compat
- **Not OpenAI gpt-4** — course used OpenAI; we use repo-root `.env`
- Related curriculum: [`../AutoGen Labs/`](../AutoGen%20Labs/)

**Not medical advice. Not therapy or crisis care.** Seek licensed professionals for real concerns; use emergency services if needed.

## Setup

```powershell
cd "Healthcare Chatbot"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Repo-root `.env`: `GROQ_API_KEY` (or Ollama).

## Run

```powershell
python app.py
```

Open http://127.0.0.1:7871

## Reference

[`reference/original-lab-notes.md`](reference/original-lab-notes.md)
