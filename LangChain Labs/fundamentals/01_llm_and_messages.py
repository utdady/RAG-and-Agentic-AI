"""01 — LLM wrap + chat messages (Human / System / AI)."""

from __future__ import annotations

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from _bootstrap import banner
from shared.llm import get_llm_info

banner("01 LLM and messages")
llm, info = get_llm_info(temperature=0.2)
print(f"Using {info.provider}:{info.model}\n")

print("--- plain invoke ---")
print(llm.invoke("Who is man's best friend?").content)

print("\n--- system + human ---")
msg = llm.invoke(
    [
        SystemMessage(
            content=(
                "You are a helpful AI bot that assists a user in choosing "
                "the perfect book to read in one short sentence"
            )
        ),
        HumanMessage(content="I enjoy mystery novels, what should I read?"),
    ]
)
print(msg.content)

print("\n--- multi-turn ---")
msg = llm.invoke(
    [
        SystemMessage(
            content=(
                "You are a supportive AI bot that suggests fitness activities "
                "to a user in one short sentence"
            )
        ),
        HumanMessage(content="I like high-intensity workouts, what should I do?"),
        AIMessage(content="You should try a CrossFit class"),
        HumanMessage(content="How often should I attend?"),
    ]
)
print(msg.content)

print("\n--- human only ---")
print(llm.invoke([HumanMessage(content="What month follows June?")]).content)
