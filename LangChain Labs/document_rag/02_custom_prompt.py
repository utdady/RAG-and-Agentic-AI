"""02 — RetrievalQA with a grounded custom PromptTemplate."""

from __future__ import annotations

from langchain.chains import RetrievalQA
from langchain_core.prompts import PromptTemplate

from _bootstrap import banner
from _rag import build_vectorstore, ensure_policies
from shared.llm import get_llm_info

banner("02 Custom prompt")
llm, _ = get_llm_info(temperature=0.5)

prompt_template = """Use the information from the document to answer the question at the end.
If you don't know the answer, just say that you don't know, definitely do not try to make up an answer.

{context}

Question: {question}
"""

PROMPT = PromptTemplate(
    template=prompt_template,
    input_variables=["context", "question"],
)

store = build_vectorstore(ensure_policies(), collection_name="policies_prompt")
qa = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=store.as_retriever(),
    chain_type_kwargs={"prompt": PROMPT},
    return_source_documents=False,
)

for query in [
    "Can I eat in company vehicles?",
    "What I cannot do in it?",
]:
    print(f"\nQ: {query}")
    result = qa.invoke(query)
    print("A:", result["result"] if isinstance(result, dict) else result)
