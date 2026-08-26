# Multi-Agent AI Systems (CrewAI) — original lab notes

Course: CrewAI 0.80 + crewai-tools SerperDevTool + Watsonx Llama 3.3 via
`crewai.LLM(model="watsonx/...")`. Sequential Process: research → writer,
then extended with social media agent.

## Install (course)

```
langchain, crewai, langchain-community, crewai-tools, databricks-sdk
```

`databricks-sdk` unused in the pasted cells — omitted here.

## Security

Notebook hardcoded `SERPER_API_KEY` — **never commit**. Use `.env` and rotate
any key that was pasted into chat.

## Flow

1. `SerperDevTool` web search on topic
2. Research analyst agent + research task
3. Writer agent + blog task
4. Optional social strategist + social posts task
5. `crew.kickoff(inputs={"topic": ...})` → `result.raw`, `tasks_output`, token usage

## This repo

`01_research_writer_crew.py` with Groq/Ollama LLM mapping and `--topic` / `--no-social` CLI.

---

# Tools versus Tasks with Tools

Course: CrewAI + `PDFSearchTool` (HuggingFace MiniLM) + `SerperDevTool` on
The Daily Dish FAQ. Compares:
1. **Agent-centric** � tools attached to the Agent
2. **Task-centric** � tools attached to Tasks; agent `tools=[]`
3. Custom `@tool` add/multiply calculator

Watsonx Granite ? Groq/Ollama. Hardcoded Serper keys omitted (use `.env`).

**This repo:** `02_tools_vs_tasks.py` with `--mode agent|task|calc|all`.
