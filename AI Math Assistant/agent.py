"""LangGraph ReAct agent factory for AI Math Assistant."""

from __future__ import annotations

from functools import lru_cache

from langgraph.prebuilt import create_react_agent

from shared.llm import get_llm_info
from tools import ALL_TOOLS, SYSTEM_PROMPT


@lru_cache(maxsize=1)
def get_math_agent():
    """Build (and cache) the LangGraph math agent on first use."""
    llm, info = get_llm_info(temperature=0)
    agent = create_react_agent(
        model=llm,
        tools=ALL_TOOLS,
        prompt=SYSTEM_PROMPT,
    )
    return agent, info


def run_query(user_text: str, history_messages: list | None = None) -> tuple[str, list]:
    """
    Invoke the agent with optional prior LangChain-style messages.

    Returns (final_assistant_text, full_messages_list).
    """
    agent, _ = get_math_agent()
    messages = list(history_messages or [])
    messages.append(("human", user_text))
    result = agent.invoke({"messages": messages})
    out_msgs = result.get("messages") or []
    final = ""
    if out_msgs:
        last = out_msgs[-1]
        final = getattr(last, "content", None) or str(last)
    return str(final), out_msgs


def describe_agent() -> str:
    _, info = get_math_agent()
    return f"{info.provider}:{info.model} (tier={info.tier})"
