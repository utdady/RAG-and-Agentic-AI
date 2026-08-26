"""04 — Reflection agent (MessageGraph): generate LinkedIn post ↔ critique loop.

Course: Watsonx + MessageGraph + pygraphviz diagram.
Here: shared.llm; print ASCII graph instead of draw_png.
"""

from __future__ import annotations

from typing import List, Sequence

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import END, MessageGraph

from _bootstrap import banner
from shared.llm import get_llm_info

banner("04 Reflection agent (LinkedIn post)")

llm, info = get_llm_info(temperature=0.4)
print(f"Using {info.provider}:{info.model}")

generation_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a professional LinkedIn content assistant tasked with crafting "
            "engaging, insightful, and well-structured LinkedIn posts. "
            "Generate the best LinkedIn post possible for the user's request. "
            "If the user provides feedback or critique, respond with a refined version "
            "of your previous attempts, improving clarity, tone, or engagement as needed.",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)
generate_chain = generation_prompt | llm

reflection_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are a professional LinkedIn content strategist and thought leadership expert.
Critically evaluate the LinkedIn post in the conversation and provide a constructive critique:
strengths, weaknesses, engagement potential, formatting/hashtags/CTA, and actionable revisions.
Your critique will drive the next rewrite — be specific and practical.""",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)
reflect_chain = reflection_prompt | llm

MAX_MESSAGES = 6  # stop after enough generate/reflect turns


def generation_node(state: Sequence[BaseMessage]) -> List[BaseMessage]:
    generated = generate_chain.invoke({"messages": state})
    content = getattr(generated, "content", None) or str(generated)
    return [AIMessage(content=content)]


def reflection_node(messages: Sequence[BaseMessage]) -> List[BaseMessage]:
    # Critique returned as HumanMessage so the generator treats it as user feedback
    res = reflect_chain.invoke({"messages": messages})
    content = getattr(res, "content", None) or str(res)
    return [HumanMessage(content=content)]


def should_continue(state: List[BaseMessage]):
    print(f"[should_continue] messages={len(state)}")
    if len(state) > MAX_MESSAGES:
        return END
    return "reflect"


def build_app():
    graph = MessageGraph()
    graph.add_node("generate", generation_node)
    graph.add_node("reflect", reflection_node)
    graph.set_entry_point("generate")
    graph.add_conditional_edges("generate", should_continue)
    graph.add_edge("reflect", "generate")
    return graph.compile()


DEMO_PROMPT = (
    "Write a LinkedIn post on getting a software developer job at IBM "
    "under 160 characters"
)


if __name__ == "__main__":
    workflow = build_app()

    try:
        print("\nGraph (mermaid):\n", workflow.get_graph().draw_mermaid())
    except Exception as e:
        print(f"(Could not render mermaid graph: {e})")

    print("\n--- Running reflection loop ---")
    response = workflow.invoke(HumanMessage(content=DEMO_PROMPT))

    if isinstance(response, list):
        messages = response
    else:
        messages = list(response) if response else []

    for i, msg in enumerate(messages):
        role = type(msg).__name__
        text = getattr(msg, "content", str(msg))
        preview = text if len(text) < 400 else text[:400] + "…"
        print(f"\n[{i}] {role}:\n{preview}")

    if messages:
        print("\n===== Final post =====\n")
        print(getattr(messages[-1], "content", messages[-1]))
