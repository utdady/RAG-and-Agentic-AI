# Agentic AI Systems with the BeeAI Framework

Course: BeeAI `RequirementAgent` progression (chat → templates → structured output → tools → requirements → custom tool → multi-agent handoffs).

## Course stack

- `beeai-framework[wikipedia]==0.1.35` (pinned in Skills Network; we allow `>=0.1.35,<0.2`)
- Watsonx Granite / Llama via `ChatModel.from_name("watsonx:…")`
- OpenAI `gpt-5-nano` for structured output demo
- Tools: Wikipedia, Think, OpenMeteo, Handoff, custom calculator
- Requirements: `ConditionalRequirement`, `AskPermissionRequirement`
- Middleware: `GlobalTrajectoryMiddleware`

## This repo

**Clubbed:** `BeeAI Labs/` (curriculum CLI — not a Gradio product; not mixed into CrewAI/LangChain Labs).

| Course | Here |
|--------|------|
| `t1`–`t12` | `01_…`–`12_…` |
| watsonx / openai model strings | `groq:…` or `ollama:…` via `_bootstrap.get_chat_model()` |
| `llm.create` / `create_structure` | Also supports newer `llm.run` / `response_format` |
| Skills Network env presets | Repo-root `.env` |

Run from `BeeAI Labs/` after `pip install -r requirements.txt`.
