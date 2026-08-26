# LangGraph 101

Intro to **LangGraph `StateGraph`**: TypedDict state, nodes, edges, routers, loops.

Course Watsonx / OpenAI → Groq/Ollama via [`../../shared/llm.py`](../../shared/llm.py) (QA script only).

Prebuilt ReAct agents live in product apps (`AI Math Assistant`, etc.); this folder builds graphs by hand.

## Run

From `LangChain Labs/` (venv + `pip install -r requirements.txt`):

```powershell
cd langgraph_101
python 01_auth_graph.py
python 02_qa_graph.py
python 03_loop_graph.py
```

## Scripts

| Script | Topic |
|--------|--------|
| `01_auth_graph.py` | Auth validate → success / failure |
| `02_qa_graph.py` | Validate → context → LLM |
| `03_loop_graph.py` | Conditional loop until `n >= 13` |

## Reference

[`reference/original-lab-notes.md`](reference/original-lab-notes.md)
