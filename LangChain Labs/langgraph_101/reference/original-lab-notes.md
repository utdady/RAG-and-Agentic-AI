# LangGraph 101 — original lab notes

Course: `langgraph==0.2.57` + Watsonx / optional OpenAI. Notebook walks
`StateGraph` with three mini-apps.

## 1. Auth graph

- `AuthState`: username, password, is_authenticated, output
- Nodes: input (`input()` prompts), validate (`test_user` / `secure_password`),
  success, failure
- Conditional router after validate; failure edge back to input (retry loop)
- Duplicate `InputNode → Validate` edge in the paste (harmless)

**This repo:** non-interactive invoke; single attempt then END.

## 2. QA graph

- `QAState`: question, context, answer
- Validate → keyword context for “langgraph” / “guided project” → Watsonx LLM
- Unrelated questions get null context → fallback answer

**This repo:** `shared.llm`; `valid`/`error` on state; HumanMessage invoke.

## 3. Loop graph

- `ChainState`: n, letter
- add random letter / increment → print → stop when `n >= 13`
- Course mapped `True`/`False` from a bool predicate

**This repo:** string router `"end"` / `"continue"`.

## Layout

`01_auth_graph.py`, `02_qa_graph.py`, `03_loop_graph.py`

---

# Reflection Agent (MessageGraph)

Course: generate LinkedIn post ? reflect as critique (`HumanMessage`) ? revise;
stop when `len(state) > 6`. Watsonx Granite + optional `pygraphviz` / `draw_png`.

Pattern:
- `generation_prompt | llm` / `reflection_prompt | llm`
- `MessageGraph`: entry `generate`, conditional ? `reflect` or `END`, edge `reflect ? generate`
- Critique as `HumanMessage` so the next generate sees feedback as user input

**This repo:** `04_reflection_agent.py`; mermaid text instead of PNG; `shared.llm`.
Not the Icebreaker Bot (profile RAG).
