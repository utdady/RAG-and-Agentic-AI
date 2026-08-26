"""
PDF Document QA Bot (RAG)
Upload PDF → chunk → local embeddings → Chroma → Groq/Ollama answers → Gradio

Course pivot: Watsonx Mistral/Slate → shared.llm + shared.embeddings
"""

from __future__ import annotations

import os
import sys
import warnings
from pathlib import Path

import gradio as gr
from langchain.chains import RetrievalQA
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shared.embeddings import get_embedding_model, resolve_embedding_model
from shared.env_load import load_env
from shared.llm import describe_setup, get_llm_info

load_env(HERE)
llm, llm_info = get_llm_info(temperature=0.5)
embeddings = get_embedding_model()
print(describe_setup())
print(f"Embeddings={resolve_embedding_model()}")

# Cache retrievers by (path, mtime) so we don't rebuild Chroma every question
_retriever_cache: dict[tuple[str, float], object] = {}

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))


def _pdf_path(file) -> Path:
    if file is None:
        raise ValueError("Upload a PDF first.")
    if isinstance(file, (str, Path)):
        return Path(file)
    # Gradio File object / tempfile
    name = getattr(file, "name", None) or getattr(file, "path", None) or str(file)
    return Path(name)


def document_loader(path: Path):
    return PyPDFLoader(str(path)).load()


def text_splitter(data):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
    )
    return splitter.split_documents(data)


def get_retriever(path: Path):
    key = (str(path.resolve()), path.stat().st_mtime)
    if key in _retriever_cache:
        return _retriever_cache[key]

    docs = document_loader(path)
    chunks = text_splitter(docs)
    vectordb = Chroma.from_documents(
        chunks,
        embeddings,
        collection_name=f"pdf_qa_{abs(hash(key[0])) % 10_000_000}",
    )
    retriever = vectordb.as_retriever()
    _retriever_cache[key] = retriever
    return retriever


def retriever_qa(file, query: str) -> str:
    if not (query or "").strip():
        return "Enter a question."
    try:
        path = _pdf_path(file)
        if not path.exists():
            return f"File not found: {path}"
        if path.suffix.lower() != ".pdf":
            return "Please upload a .pdf file."

        retriever = get_retriever(path)
        qa = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=False,
        )
        response = qa.invoke(query)
        if isinstance(response, dict):
            return response.get("result", str(response))
        return str(response)
    except Exception as e:
        return f"Error: {e}"


rag_application = gr.Interface(
    fn=retriever_qa,
    inputs=[
        gr.File(
            label="Upload PDF File",
            file_count="single",
            file_types=[".pdf"],
            type="filepath",
        ),
        gr.Textbox(
            label="Input Query",
            lines=2,
            placeholder="Type your question here...",
        ),
    ],
    outputs=gr.Textbox(label="Output", lines=8),
    title="PDF RAG Chatbot",
    description=(
        f"Upload a PDF and ask questions grounded in that document. "
        f"({llm_info.provider}:{llm_info.model}; embeddings={resolve_embedding_model()})"
    ),
    allow_flagging="never",
)

if __name__ == "__main__":
    rag_application.launch(server_name="127.0.0.1", server_port=7863, share=False)
