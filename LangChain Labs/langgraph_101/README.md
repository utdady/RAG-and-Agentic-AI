# LangGraph 101

Intro to **LangGraph**: `StateGraph` basics plus a **MessageGraph** reflection loop.

Course Watsonx → Groq/Ollama via [`../../shared/llm.py`](../../shared/llm.py).

Prebuilt ReAct agents live in product apps (`AI Math Assistant`, etc.); this folder builds graphs by hand.

## Run

From `LangChain Labs/` (venv + `pip install -r requirements.txt`):

```powershell
cd langgraph_101
python 01_auth_graph.py
python 02_qa_graph.py
python 03_loop_graph.py
python 04_reflection_agent.py
```

## Scripts

| Script | Topic |
|--------|--------|
| `01_auth_graph.py` | Auth validate → success / failure |
| `02_qa_graph.py` | Validate → context → LLM |
| `03_loop_graph.py` | Conditional loop until `n >= 13` |
| `04_reflection_agent.py` | LinkedIn post generate ↔ reflect loop |

## Reference

[`reference/original-lab-notes.md`](reference/original-lab-notes.md)
