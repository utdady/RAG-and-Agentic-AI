# LangGraph 101 â€” original lab notes

Course: `langgraph==0.2.57` + Watsonx / optional OpenAI. Notebook walks
`StateGraph` with three mini-apps.

## 1. Auth graph

- `AuthState`: username, password, is_authenticated, output
- Nodes: input (`input()` prompts), validate (`test_user` / `secure_password`),
  success, failure
- Conditional router after validate; failure edge back to input (retry loop)
- Duplicate `InputNode â†’ Validate` edge in the paste (harmless)

**This repo:** non-interactive invoke; single attempt then END.

## 2. QA graph

- `QAState`: question, context, answer
- Validate â†’ keyword context for â€œlanggraphâ€ / â€œguided projectâ€ â†’ Watsonx LLM
- Unrelated questions get null context â†’ fallback answer

**This repo:** `shared.llm`; `valid`/`error` on state; HumanMessage invoke.

## 3. Loop graph

- `ChainState`: n, letter
- add random letter / increment â†’ print â†’ stop when `n >= 13`
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

---

# Reflection + External Knowledge (Tavily)

Course: OpenAI `gpt-4.1-nano` + `TavilySearchResults` + MessageGraph:
`respond` (`AnswerQuestion` tool schema) ? `execute_tools` ? `revisor` (`ReviseAnswer`)
? loop until `MAX_ITERATIONS` tool visits. Opinionated carnivore-MD style system prompt.

**Do not commit Tavily keys.** Course paste included a plaintext `tvly-…` key — rotate if exposed.

**This repo:** `05_reflection_with_search.py`; `TAVILY_API_KEY` via `.env`; `shared.llm`;
softer disclaimer (not medical advice); default `REFLECT_SEARCH_MAX_ITERS=2` (course used 4).

---

# Reasoning and Acting (ReAct) with LangGraph

Course: OpenAI + Tavily `search_tool`, `recommend_clothing`, then exercises for
safe `calculator_tool` (AST) and `news_summarizer_tool`.
`AgentState` with `add_messages`; nodes `agent` / `tools`; conditional continue|end.

Hardcoded Tavily keys in the notebook — **never commit**; use `.env`.

**This repo:** `06_react_agent.py` with all four tools wired; `shared.llm`; mermaid graph.
Vs `fundamentals/09_agents.py` (LangChain AgentExecutor) and product `create_react_agent` apps.

---

# Workflow patterns with LangGraph

Course: OpenAI `gpt-4o-mini` (+ `httpx` verify=False) and `pygraphviz`.

Patterns:
1. Sequential chain — resume summary ? cover letter
2. Router — summarize vs translate via `bind_tools`
3. Parallel — `START` ? FR/ES/JA ? aggregator ? `END`
4. Exercise — ride / restaurant / groceries / default_handler router

**This repo:** `07_workflow_patterns.py`; `shared.llm`; edges to `END` instead of
`set_finish_point`; mermaid instead of PNG.

---

# LangGraph Design Patterns

Course: OpenAI `gpt-4o-mini`, optional litellm `ssl_verify=False`, pygraphviz.

## A) Orchestrator–worker
- `Dishes` structured plan from meals
- `Send("chef_worker", …)` fan-out; `completed_menu` with `operator.add`
- `synthesizer` joins worker outputs

## B) Evaluator–optimizer
- Target risk grade from profile
- Initial bold plan ? evaluator structured `Feedback`
- Route accept vs regenerate until grade matches (or iteration cap)

**This repo:** `08_design_patterns.py`; `shared.llm`; educational disclaimers; no litellm.
