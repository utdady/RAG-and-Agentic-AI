# AI Math Assistant

Gradio chat app: LangGraph ReAct agent with arithmetic tools + Wikipedia.

- **LLM:** Groq / Ollama via [`../shared/llm.py`](../shared/llm.py)
- **Not Watsonx / OpenAI** — course used Granite on watsonx.ai and optional GPT for function-calling demos
- **Not** the thin ReAct intro in `LangChain Labs/fundamentals/09_agents.py` — this is the multi-tool math + wiki product

## Setup

```powershell
cd "AI Math Assistant"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Ensure `GROQ_API_KEY` (or Ollama) in repo-root `.env`.

## Run

```powershell
python app.py
```

Open http://127.0.0.1:7863

## Tools

| Tool | Behavior |
|------|----------|
| `add_numbers` | Sum all numbers in the query text |
| `subtract_numbers` | First − second − … |
| `multiply_numbers` | Product of all numbers |
| `divide_numbers` | First ÷ second ÷ … |
| `calculate_power` | `5^2`, `5 2`, or “5 to the power of 2” |
| `search_wikipedia` | Fact lookup (custom Wikipedia user-agent) |

Example: *“What is the population of Canada? Multiply it by 0.75”* → wiki then multiply.

## Reference

[`reference/original-lab-notes.md`](reference/original-lab-notes.md)
