"""06 — Hand-built ReAct agent (StateGraph): agent ↔ tools.

Course: OpenAI + Tavily + clothing tool + calculator/news exercises.
Here: shared.llm + TAVILY_API_KEY from .env (never hardcode keys).
"""

from __future__ import annotations

import ast
import json
import math
import operator
import os
from typing import Annotated, Sequence, TypedDict

from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages

from _bootstrap import banner
from shared.llm import get_llm_info, resolve_provider

banner("06 ReAct agent (LangGraph StateGraph)")

if not os.getenv("TAVILY_API_KEY", "").strip():
    raise SystemExit("Set TAVILY_API_KEY in repo-root .env")

if resolve_provider() == "ollama":
    print("Warning: tool-calling works more reliably with Groq.")

llm, info = get_llm_info(temperature=0)
print(f"Using {info.provider}:{info.model}")

search = TavilySearchResults(max_results=3)


@tool
def search_tool(query: str):
    """Search the web for information using Tavily API."""
    return search.invoke(query)


@tool
def recommend_clothing(weather: str) -> str:
    """Return a clothing recommendation from a short weather description."""
    w = (weather or "").lower()
    if "snow" in w or "freezing" in w:
        return "Wear a heavy coat, gloves, and boots."
    if "rain" in w or "wet" in w:
        return "Bring a raincoat and waterproof shoes."
    if "hot" in w or "85" in w:
        return "T-shirt, shorts, and sunscreen recommended."
    if "cold" in w or "50" in w:
        return "Wear a warm jacket or sweater."
    return "A light jacket should be fine."


SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
}
SAFE_FUNCTIONS = {
    "sqrt": math.sqrt,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "pi": math.pi,
}


def _eval_ast(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.Num):  # pragma: no cover — py<3.8
        return node.n
    if isinstance(node, ast.BinOp) and type(node.op) in SAFE_OPERATORS:
        return SAFE_OPERATORS[type(node.op)](
            _eval_ast(node.left), _eval_ast(node.right)
        )
    if isinstance(node, ast.UnaryOp) and type(node.op) in SAFE_OPERATORS:
        return SAFE_OPERATORS[type(node.op)](_eval_ast(node.operand))
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        name = node.func.id
        if name not in SAFE_FUNCTIONS or not callable(SAFE_FUNCTIONS[name]):
            raise ValueError(f"Function '{name}' is not supported.")
        return SAFE_FUNCTIONS[name](*[_eval_ast(a) for a in node.args])
    if isinstance(node, ast.Name) and node.id in SAFE_FUNCTIONS:
        return SAFE_FUNCTIONS[node.id]
    raise TypeError(f"Unsupported: {type(node).__name__}")


@tool
def calculator_tool(expression: str) -> str:
    """
    Safely evaluate math: +, -, *, /, **, sqrt(), sin(), cos(), tan(), pi.
    Example: "0.15 * 250 + sqrt(144)"
    """
    try:
        # Allow percent shorthand from LLMs: "15%" → "0.15"
        expr = (expression or "").replace(" ", "")
        expr = expr.replace("%", "*0.01")
        tree = ast.parse(expr, mode="eval")
        return str(_eval_ast(tree.body))
    except Exception as e:
        return f"Error evaluating expression '{expression}': {e}"


@tool
def news_summarizer_tool(news_content: str) -> str:
    """Summarize news search results (JSON list/dict or plain text) into top items."""
    if not (news_content or "").strip():
        return "No news content was provided to summarize."

    articles = []
    try:
        data = json.loads(news_content)
        if isinstance(data, list):
            articles = data[:3]
        elif isinstance(data, dict) and "results" in data:
            articles = data["results"][:3]
    except (json.JSONDecodeError, TypeError):
        blocks = [b.strip() for b in news_content.split("\n\n") if b.strip()]
        for i, block in enumerate(blocks[:3]):
            articles.append(
                {"title": f"Article Item {i + 1}", "url": "N/A", "content": block}
            )

    if not articles:
        return "Could not extract structured news information."

    lines = ["### Recent News Summary (Top 3)\n---"]
    for idx, art in enumerate(articles, 1):
        title = str(art.get("title") or art.get("headline") or "Untitled").strip()
        url = str(art.get("url") or art.get("link") or "Unknown").strip()
        content = str(
            art.get("content") or art.get("snippet") or "No content."
        ).strip()
        sentences = [s.strip() for s in content.split(". ") if s.strip()]
        points = "\n   - ".join(sentences[:2]) if sentences else "N/A"
        lines.append(
            f"**{idx}. {title}**\n"
            f"Source: {url}\n"
            f"Key takeaways:\n   - {points}\n"
        )
    return "\n".join(lines)


tools = [search_tool, recommend_clothing, calculator_tool, news_summarizer_tool]
tools_by_name = {t.name: t for t in tools}

chat_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a helpful AI assistant that thinks step-by-step and uses tools when needed.

When responding:
1. Think about what information you need
2. Use tools for current data, math, clothing advice from weather text, or news summaries
3. Give a clear final answer

For percent questions, convert to decimals in calculator_tool (e.g. 15% of 250 → 0.15*250).
For "calculate X plus sqrt(Y)", pass a single expression like "0.15*250+sqrt(144)".
""",
        ),
        MessagesPlaceholder(variable_name="scratch_pad"),
    ]
)
model_react = chat_prompt | llm.bind_tools(tools)


class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], add_messages]


def tool_node(state: AgentState):
    outputs = []
    last = state["messages"][-1]
    for tool_call in getattr(last, "tool_calls", None) or []:
        result = tools_by_name[tool_call["name"]].invoke(tool_call["args"])
        outputs.append(
            ToolMessage(
                content=json.dumps(result)
                if not isinstance(result, str)
                else result,
                name=tool_call["name"],
                tool_call_id=tool_call["id"],
            )
        )
    return {"messages": outputs}


def call_model(state: AgentState):
    response = model_react.invoke({"scratch_pad": state["messages"]})
    return {"messages": [response]}


def should_continue(state: AgentState):
    last = state["messages"][-1]
    return "continue" if getattr(last, "tool_calls", None) else "end"


def build_graph():
    workflow = StateGraph(AgentState)
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", tool_node)
    workflow.set_entry_point("agent")
    workflow.add_edge("tools", "agent")
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {"continue": "tools", "end": END},
    )
    return workflow.compile()


def print_stream(stream):
    for s in stream:
        message = s["messages"][-1]
        if hasattr(message, "pretty_print"):
            message.pretty_print()
        else:
            print(type(message).__name__, getattr(message, "content", message))


DEMOS = [
    "What's the weather like in Zurich, and what should I wear based on the temperature?",
    "Calculate 15% of 250 plus the square root of 144",
    "Find recent AI news and summarize the top 3 articles",
]


if __name__ == "__main__":
    graph = build_graph()
    try:
        print("\nGraph (mermaid):\n", graph.get_graph().draw_mermaid())
    except Exception as e:
        print(f"(mermaid unavailable: {e})")

    for q in DEMOS:
        print(f"\n{'=' * 60}\nQ: {q}\n{'=' * 60}")
        print_stream(
            graph.stream(
                {"messages": [HumanMessage(content=q)]},
                stream_mode="values",
            )
        )
