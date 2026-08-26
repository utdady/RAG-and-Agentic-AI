"""03 — Loop StateGraph: add → print → continue|END until n >= 13."""

from __future__ import annotations

import random
import string
from typing import TypedDict

from langgraph.graph import END, StateGraph

from _bootstrap import banner

banner("03 Loop graph")


class ChainState(TypedDict):
    n: int
    letter: str


def add(state: ChainState) -> dict:
    return {
        "n": state["n"] + 1,
        "letter": random.choice(string.ascii_lowercase),
    }


def print_out(state: ChainState) -> dict:
    print(f"Current n: {state['n']} Letter: {state['letter']}")
    return {}


def stop_router(state: ChainState) -> str:
    # Prefer string routes over bool keys (clearer across LangGraph versions)
    return "end" if state["n"] >= 13 else "continue"


def build_app():
    workflow = StateGraph(ChainState)
    workflow.add_node("add", add)
    workflow.add_node("print", print_out)
    workflow.set_entry_point("add")
    workflow.add_edge("add", "print")
    workflow.add_conditional_edges(
        "print",
        stop_router,
        {"end": END, "continue": "add"},
    )
    return workflow.compile()


if __name__ == "__main__":
    app = build_app()
    result = app.invoke({"n": 1, "letter": ""})
    print("\nFinal state:", result)
