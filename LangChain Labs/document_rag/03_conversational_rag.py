"""03 — Conversational RAG with chat memory (follow-up questions)."""

from __future__ import annotations

import sys

from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

from _bootstrap import banner
from _rag import build_vectorstore, ensure_policies, ensure_state_of_union
from shared.llm import get_llm_info

banner("03 Conversational RAG")
llm, _ = get_llm_info(temperature=0.5)

store = build_vectorstore(ensure_policies(), collection_name="policies_chat")

# Original lab typo: return_message → return_messages
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True,
    output_key="answer",
)

qa = ConversationalRetrievalChain.from_llm(
    llm=llm,
    chain_type="stuff",
    retriever=store.as_retriever(),
    memory=memory,
    return_source_documents=False,
)

scripted = [
    "What is mobile policy?",
    "List points in it?",
    "What is the aim of it?",
]

print("--- scripted follow-ups ---")
for query in scripted:
    print(f"\nQ: {query}")
    result = qa.invoke({"question": query})
    print("A:", result.get("answer", result))

# Optional: State of the Union ingest smoke-test (course exercise asset)
if "--sotu" in sys.argv:
    print("\n--- State of the Union (optional) ---")
    sotu = ensure_state_of_union()
    sotu_store = build_vectorstore(sotu, collection_name="sotu")
    sotu_qa = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=sotu_store.as_retriever(),
        memory=ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer",
        ),
    )
    r = sotu_qa.invoke({"question": "Summarize the main themes in a few sentences."})
    print(r.get("answer", r))

# Interactive REPL unless --no-repl
if "--no-repl" not in sys.argv:
    print("\n--- interactive (quit / exit / bye to leave) ---")
    # Fresh memory for the live session
    live_memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="answer",
    )
    live = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=store.as_retriever(),
        memory=live_memory,
    )
    while True:
        try:
            query = input("Question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nAnswer: Goodbye!")
            break
        if query.lower() in {"quit", "exit", "bye"}:
            print("Answer: Goodbye!")
            break
        result = live.invoke({"question": query})
        print("Answer:", result.get("answer", result))
