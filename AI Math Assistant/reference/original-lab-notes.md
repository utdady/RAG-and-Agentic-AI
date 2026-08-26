# AI Math Assistant — original lab notes (Watsonx / OpenAI → Groq/Ollama)

Course notebook: LangChain tools, classic `initialize_agent`, then LangGraph
`create_react_agent`, arithmetic tools, Wikipedia, and a PowerTool exercise.

## Install (course)

```
langchain, langchain-ibm, langchain-community, wikipedia,
openai, langchain-openai, langgraph
```

## LLM (course)

- Primary: `ChatWatsonx` (`ibm/granite-4-h-small`, skills-network project)
- Optional local: `ChatOpenAI(gpt-4.1-nano)` for openai-functions agents

**This repo:** `shared.llm.get_chat_llm` / `get_llm_info` (Groq or Ollama).

## Tool construction

1. Manual `Tool(name=..., func=..., description=...)` wrapping `add_numbers`
2. `@tool` decorator — auto schema / args
3. Typed `@tool` with `List[float]` + optional `absolute` flag
4. Complex return types (`Dict[str, Union[float, str]]`)

Number extraction evolved from `str.isdigit()` splits → `re.findall` for decimals/negatives.

## Classic agents (legacy in notebook)

```
initialize_agent(..., agent="zero-shot-react-description")
initialize_agent(..., agent="structured-chat-zero-shot-react-description")
initialize_agent(..., agent="openai-functions")  # needs OpenAI
```

GDP-style natural-language sum demos; parsing-error handling enabled.

**This repo:** skipped in the Gradio app; prefer LangGraph only.

## LangGraph math agent

```python
from langgraph.prebuilt import create_react_agent
math_agent = create_react_agent(model=llm, tools=[...], prompt="...")
math_agent.invoke({"messages": [("human", "...")]})
```

Tools: add / subtract (initially negated-first quirk) / multiply / divide.
Later fixed to sequential subtract: `a - b - c`.

Test harness checked tool message JSON `result` against expected values.

## Wikipedia

```python
WikipediaAPIWrapper + @tool search_wikipedia
wikipedia.set_user_agent("...")  # avoid blocks
```

Hybrid query: Canada population × 0.75.

## Exercise (TODO in notebook)

`calculate_power` + `Tool` / `ZERO_SHOT_REACT_DESCRIPTION` agent for “5 to the power of 2”.

**This repo:** implemented as `@tool calculate_power` on the LangGraph agent (not classic initialize_agent).

## Product layout here

| File | Role |
|------|------|
| `tools.py` | All tools + system prompt |
| `agent.py` | Cached `create_react_agent` |
| `app.py` | Gradio chat UI (port 7863) |
