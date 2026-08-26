"""10 — Manual tool-calling loop (bind_tools → ToolMessage → answer).

Course: Interactive LLM Agents (OpenAI / Watsonx).
Here: Groq/Ollama via shared.llm. Complements 09_agents (ReAct executor)
by showing the plumbing under tool use.
"""

from __future__ import annotations

from langchain_core.messages import HumanMessage, ToolMessage
from langchain_core.tools import tool

from _bootstrap import banner
from shared.llm import get_llm_info

banner("10 Tool-calling loop (manual)")

llm, info = get_llm_info(temperature=0)
print(f"Using {info.provider}:{info.model}")


@tool
def add(a: int, b: int) -> int:
    """Add a and b."""
    return a + b


@tool
def subtract(a: int, b: int) -> int:
    """Subtract b from a."""
    return a - b


@tool
def multiply(a: int, b: int) -> int:
    """Multiply a and b."""
    return a * b


@tool
def calculate_tip(total_bill: float, tip_percent: float) -> float:
    """Calculate tip amount from total_bill and tip_percent (e.g. 20 for 20%)."""
    return total_bill * tip_percent * 0.01


MATH_TOOLS = [add, subtract, multiply]
MATH_TOOL_MAP = {t.name: t for t in MATH_TOOLS}


class ToolCallingAgent:
    """Single-step tool agent: at most one tool call, then final answer."""

    def __init__(self, chat_llm, tools: list):
        self.tools = tools
        self.tool_map = {t.name: t for t in tools}
        self.llm_with_tools = chat_llm.bind_tools(tools)

    def run(self, query: str) -> str:
        chat_history = [HumanMessage(content=query)]
        response = self.llm_with_tools.invoke(chat_history)

        if not getattr(response, "tool_calls", None):
            return response.content or str(response)

        # Handle first tool call (course lab did one call only)
        tool_call = response.tool_calls[0]
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        tool_call_id = tool_call["id"]

        if tool_name not in self.tool_map:
            return f"Unknown tool: {tool_name}"

        tool_result = self.tool_map[tool_name].invoke(tool_args)
        tool_message = ToolMessage(
            content=str(tool_result), tool_call_id=tool_call_id
        )
        chat_history.extend([response, tool_message])
        final = self.llm_with_tools.invoke(chat_history)
        return final.content or str(final)


def demo_manual_roundtrip() -> None:
    """Show bind_tools + ToolMessage without the agent class."""
    print("\n--- Manual round-trip ---")
    llm_with_tools = llm.bind_tools(MATH_TOOLS)
    history = [HumanMessage(content="What is 1 plus 2?")]
    response = llm_with_tools.invoke(history)
    print(f"AIMessage type={type(response).__name__}")
    if not response.tool_calls:
        print("No tool call; content:", response.content)
        return

    call = response.tool_calls[0]
    print(f"tool={call['name']} args={call['args']} id={call['id']}")
    result = MATH_TOOL_MAP[call["name"]].invoke(call["args"])
    history.extend(
        [
            response,
            ToolMessage(content=str(result), tool_call_id=call["id"]),
        ]
    )
    answer = llm_with_tools.invoke(history)
    print("Final:", answer.content)


def demo_math_agent() -> None:
    print("\n--- ToolCallingAgent (math) ---")
    agent = ToolCallingAgent(llm, MATH_TOOLS)
    for q in ("one plus 2", "one - 2", "three times two"):
        print(f"Q: {q}")
        print(f"A: {agent.run(q)}\n")


def demo_tip_agent() -> None:
    print("\n--- TipAgent ---")
    tip_tool = calculate_tip
    print("Direct invoke:", tip_tool.invoke({"total_bill": 120, "tip_percent": 15}))
    agent = ToolCallingAgent(llm, [tip_tool])
    q = "How much should I tip on $60 at 20%?"
    print(f"Q: {q}")
    print(f"A: {agent.run(q)}")


if __name__ == "__main__":
    demo_manual_roundtrip()
    demo_math_agent()
    demo_tip_agent()
    print(
        "\nNote: course notebook had typos (contet; TipAgent used module globals). "
        "This script uses a shared ToolCallingAgent for math + tip."
    )
