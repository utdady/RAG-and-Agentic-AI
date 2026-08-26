"""03 — PromptTemplate, ChatPromptTemplate, MessagesPlaceholder."""

from __future__ import annotations

from langchain_core.messages import HumanMessage
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    PromptTemplate,
)

from _bootstrap import banner
from shared.llm import get_llm_info

banner("03 Prompts")
llm, _ = get_llm_info(temperature=0.2)

# Classic string template
pt = PromptTemplate.from_template(
    "Translate the following text to {language}:\n\n{text}"
)
filled = pt.format(language="French", text="Good morning, how are you?")
print("--- PromptTemplate ---")
print(filled)
print(llm.invoke(filled).content)

# Chat-style template
chat_pt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a concise {role}."),
        ("human", "{question}"),
    ]
)
print("\n--- ChatPromptTemplate ---")
print(llm.invoke(chat_pt.format_messages(role="travel guide", question="Best day trip from Rome?")).content)

# MessagesPlaceholder for history
hist_pt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant. Keep answers short."),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ]
)
print("\n--- MessagesPlaceholder ---")
msgs = hist_pt.format_messages(
    history=[
        HumanMessage(content="My name is Ada."),
        HumanMessage(content="I like astronomy."),
    ],
    input="What is my name and interest?",
)
print(llm.invoke(msgs).content)
