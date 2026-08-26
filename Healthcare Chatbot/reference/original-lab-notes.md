# Multi Agent Chatbot with AutoGen for Healthcare

Course: AutoGen GroupChat demos for (1) symptom consultation and (2) mental health support.

## Course stack

- `autogen==0.7`, `openai`, CLI `input()`
- Agents: patient / diagnosis / pharmacy / consultation
- Mental health: patient / emotion_analysis / therapy_recommendation
- `GroupChat` + `GroupChatManager`, `speaker_selection_method="round_robin"`
- OpenAI `gpt-4` / `gpt-4o`

## This repo

**Standalone Gradio product:** `Healthcare Chatbot/` (not clubbed into AutoGen Labs).

| Course | Here |
|--------|------|
| CLI `input()` | Gradio tabs, port **7871** |
| OpenAI gpt-4 | Groq / Ollama via `llm_config.py` |
| `autogen==0.7` | `ag2[openai]>=0.8,<1` |

Strong educational disclaimers in UI and agent prompts.
