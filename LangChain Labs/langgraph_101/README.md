# LangGraph 101

Intro to **LangGraph**: `StateGraph` basics, MessageGraph reflection, and reflection + web search.

Course Watsonx/OpenAI → Groq/Ollama via [`../../shared/llm.py`](../../shared/llm.py).

Prebuilt ReAct agents live in product apps (`AI Math Assistant`, etc.); this folder builds graphs by hand.

## Run

From `LangChain Labs/` (venv + `pip install -r requirements.txt`):

```powershell
cd langgraph_101
python 01_auth_graph.py
python 02_qa_graph.py
python 03_loop_graph.py
python 04_reflection_agent.py
python 05_reflection_with_search.py   # needs TAVILY_API_KEY in repo-root .env
```

## Scripts

| Script | Topic |
|--------|--------|
| `01_auth_graph.py` | Auth validate → success / failure |
| `02_qa_graph.py` | Validate → context → LLM |
| `03_loop_graph.py` | Conditional loop until `n >= 13` |
| `04_reflection_agent.py` | LinkedIn post generate ↔ reflect loop |
| `05_reflection_with_search.py` | Structured answer → Tavily → revise loop |

`05` is an educational demo (not medical advice). Prefer Groq for `bind_tools`.

## Reference

[`reference/original-lab-notes.md`](reference/original-lab-notes.md)
