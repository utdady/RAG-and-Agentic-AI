"""03 — Capstone: structured product-review analysis with PromptTemplate + LCEL."""

from __future__ import annotations

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate

from _bootstrap import banner
from shared.llm import get_llm_info

banner("03 Review analysis")
llm, _ = get_llm_info(temperature=0.2)

template = """
Analyze the following product review:
"{review}"

Provide your analysis in the following format:
- Sentiment: (positive, negative, or neutral)
- Key Features Mentioned: (list the product features mentioned)
- Summary: (one-sentence summary)
"""

chain = PromptTemplate.from_template(template) | llm | StrOutputParser()

reviews = [
    (
        "I love this smartphone! The camera quality is exceptional and the battery "
        "lasts all day. The only downside is that it heats up a bit during gaming."
    ),
    (
        "This laptop is terrible. It's slow, crashes frequently, and the keyboard "
        "stopped working after just two months. Customer service was unhelpful."
    ),
]

for i, review in enumerate(reviews, 1):
    print(f"==== Review #{i} ====")
    print(chain.invoke({"review": review}))
    print()
