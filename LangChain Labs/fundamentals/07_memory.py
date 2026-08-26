"""07 — Conversation memory (buffer + summary) via LCEL RunnableWithMessageHistory."""

from __future__ import annotations

from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory

from _bootstrap import banner
from shared.llm import get_llm_info

banner("07 Memory")
llm, _ = get_llm_info(temperature=0.2)

# Session store (lab demo — in-memory only)
_store: dict[str, InMemoryChatMessageHistory] = {}


def get_history(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in _store:
        _store[session_id] = InMemoryChatMessageHistory()
    return _store[session_id]


prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant. Keep answers short."),
        MessagesPlaceholder("history"),
        ("human", "{input}"),
    ]
)
chain = prompt | llm

with_history = RunnableWithMessageHistory(
    chain,
    get_history,
    input_messages_key="input",
    history_messages_key="history",
)

cfg = {"configurable": {"session_id": "demo"}}
print("--- turn 1 ---")
r1 = with_history.invoke({"input": "Hi, my name is Sam and I love hiking."}, cfg)
print(r1.content)

print("\n--- turn 2 (should recall name) ---")
r2 = with_history.invoke({"input": "What is my name and hobby?"}, cfg)
print(r2.content)

print(
    "\nNote: original lab used ConversationBufferMemory / "
    "ConversationSummaryMemory. Modern LCEL uses RunnableWithMessageHistory "
    "(buffer shown). For summaries, wrap history with a summarize step."
)
