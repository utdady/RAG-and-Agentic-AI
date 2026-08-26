# AutoGen Tutorial

Course: AG2 / AutoGen multi-agent patterns in a Skills Network–style notebook.

## Course stack

- `ag2[openai]` (imports as `autogen`; use **`<1`** — 1.x is a breaking rewrite)
- OpenAI `gpt-4o-mini` via env API key
- Patterns: ConversableAgent chat, AssistantAgent + UserProxy code exec,
  human triage, GroupChat, `register_function`, Pydantic `response_format`

## This repo

**Clubbed:** `AutoGen Labs/` (curriculum CLI — not a Gradio product).

| Course | Here |
|--------|------|
| Single notebook cells | `01`–`07` scripts |
| `gpt-4o-mini` | Groq (`api_type: groq`) or Ollama OpenAI-compat |
| IPython `display(Image…)` | Print path to `coding/sine_wave.png` |
| Env OpenAI key | Repo-root `.env` `GROQ_API_KEY` |

Helper: `_bootstrap.get_llm_config()`.
