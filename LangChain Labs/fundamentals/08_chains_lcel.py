"""08 — Chains: LCEL pipe (preferred) vs SequentialChain-style two-step."""

from __future__ import annotations

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from _bootstrap import banner
from shared.llm import get_llm_info

banner("08 Chains / LCEL")
llm, _ = get_llm_info(temperature=0.3)
parser = StrOutputParser()

# --- Single LCEL chain ---
slogan = (
    ChatPromptTemplate.from_template(
        "Write one short marketing slogan for: {product}"
    )
    | llm
    | parser
)
print("--- LCEL: slogan ---")
print(slogan.invoke({"product": "noise-cancelling headphones"}))

# --- Two-step LCEL (SequentialChain equivalent) ---
outline = (
    ChatPromptTemplate.from_template(
        "List 3 bullet points about why someone would buy: {product}"
    )
    | llm
    | parser
)
expand = (
    ChatPromptTemplate.from_template(
        "Turn these product points into a short paragraph:\n{points}"
    )
    | llm
    | parser
)

print("\n--- LCEL: sequential outline → paragraph ---")
points = outline.invoke({"product": "standing desk"})
print("points:\n", points)
print("\nparagraph:\n", expand.invoke({"points": points}))

print(
    "\nNote: LLMChain / SequentialChain are legacy. Prefer `prompt | llm | parser`."
)
