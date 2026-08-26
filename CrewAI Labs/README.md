# CrewAI Labs

Curriculum labs for **CrewAI** multi-agent crews (not LangGraph).

Course Watsonx → **Groq / Ollama** via `crewai.LLM`. Search via **Serper** (`SERPER_API_KEY`).

## Setup

```powershell
cd "CrewAI Labs"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

In repo-root `.env`:

- `GROQ_API_KEY` (preferred) or Ollama
- `SERPER_API_KEY` from https://serper.dev

## Run

```powershell
python 01_research_writer_crew.py
python 01_research_writer_crew.py --topic "Edge AI chips 2026"
python 01_research_writer_crew.py --no-social
```

## Scripts

| Script | Topic |
|--------|--------|
| `01_research_writer_crew.py` | Sequential: research (Serper) → blog → social posts |

## Reference

[`reference/original-lab-notes.md`](reference/original-lab-notes.md)
