"""
Build a Smarter Search with LangChain Context Retrieval

Chroma retrievers: similarity / k / MMR / threshold → MultiQuery → SelfQuery → ParentDocument

LLM: Groq/Ollama via shared.llm | Embeddings: local MiniLM via shared.embeddings
"""

from __future__ import annotations

import logging
import sys
import tempfile
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[1]
HERE = Path(__file__).resolve().parent
DATA = HERE / "data"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

load_dotenv(HERE / ".env")
load_dotenv(ROOT / ".env")
load_dotenv(ROOT / "Meeting Assistant" / ".env")

from langchain.retrievers import ParentDocumentRetriever
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain.retrievers.self_query.base import SelfQueryRetriever
from langchain.storage import InMemoryStore
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.documents import Document
from langchain.chains.query_constructor.base import AttributeInfo
from langchain_text_splitters import CharacterTextSplitter, RecursiveCharacterTextSplitter

from shared.embeddings import get_embedding_model, resolve_embedding_model
from shared.llm import describe_setup, get_llm_info

# ensure assets
from download_data import main as download_assets

download_assets()

llm, llm_info = get_llm_info(temperature=0.2)
embeddings = get_embedding_model()
print(describe_setup())
print(f"Embeddings={resolve_embedding_model()}")
print(f"LLM={llm_info.provider}:{llm_info.model}")


def banner(title: str) -> None:
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def show_docs(docs, limit: int = 3) -> None:
    print(f"Retrieved {len(docs)} doc(s)")
    for i, d in enumerate(docs[:limit], 1):
        preview = (d.page_content or "").replace("\n", " ")[:120]
        meta = {k: d.metadata.get(k) for k in ("year", "rating", "genre", "director") if k in d.metadata}
        print(f"{i}. {preview}...")
        if meta:
            print(f"   meta={meta}")
    print()


def text_splitter(data, chunk_size: int, chunk_overlap: int):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    return splitter.split_documents(data)


def fresh_chroma(name: str, docs=None) -> Chroma:
    """Ephemeral on-disk Chroma collection (avoids mid-lab delete races)."""
    path = Path(tempfile.mkdtemp(prefix=f"chroma_{name}_"))
    if docs is not None:
        return Chroma.from_documents(
            documents=docs,
            embedding=embeddings,
            collection_name=name,
            persist_directory=str(path),
        )
    return Chroma(
        collection_name=name,
        embedding_function=embeddings,
        persist_directory=str(path),
    )


def section_basic_retrievers(chunks_txt) -> None:
    banner("1. BASIC CHROMA RETRIEVERS (company policies)")
    vectordb = fresh_chroma("policies", chunks_txt)
    query = "email policy"

    print(f"Query: {query}\n--- default retriever ---")
    show_docs(vectordb.as_retriever().invoke(query))

    print("--- k=1 ---")
    show_docs(vectordb.as_retriever(search_kwargs={"k": 1}).invoke(query))

    print("--- MMR ---")
    show_docs(vectordb.as_retriever(search_type="mmr").invoke(query))

    print("--- similarity_score_threshold (0.4) ---")
    try:
        show_docs(
            vectordb.as_retriever(
                search_type="similarity_score_threshold",
                search_kwargs={"score_threshold": 0.4},
            ).invoke(query)
        )
    except Exception as e:
        print(f"Soft-fail threshold search: {e}\n")


def section_multiquery(chunks_pdf) -> None:
    banner("2. MULTI-QUERY RETRIEVER (LangChain paper)")
    vectordb = fresh_chroma("paper", chunks_pdf)
    query = "What does the paper say about langchain?"

    logging.basicConfig()
    logging.getLogger("langchain.retrievers.multi_query").setLevel(logging.INFO)

    try:
        retriever = MultiQueryRetriever.from_llm(
            retriever=vectordb.as_retriever(),
            llm=llm,
        )
        print(f"Query: {query}")
        show_docs(retriever.invoke(query), limit=4)
    except Exception as e:
        print(f"Soft-fail MultiQuery: {e}")
        print("Fallback: plain similarity")
        show_docs(vectordb.as_retriever(search_kwargs={"k": 3}).invoke(query))


def movie_docs() -> list[Document]:
    return [
        Document(
            page_content="A bunch of scientists bring back dinosaurs and mayhem breaks loose",
            metadata={"year": 1993, "rating": 7.7, "genre": "science fiction"},
        ),
        Document(
            page_content="Leo DiCaprio gets lost in a dream within a dream within a dream within a ...",
            metadata={"year": 2010, "director": "Christopher Nolan", "rating": 8.2},
        ),
        Document(
            page_content="A psychologist / detective gets lost in a series of dreams within dreams within dreams and Inception reused the idea",
            metadata={"year": 2006, "director": "Satoshi Kon", "rating": 8.6},
        ),
        Document(
            page_content="A bunch of normal-sized women are supremely wholesome and some men pine after them",
            metadata={"year": 2019, "director": "Greta Gerwig", "rating": 8.3},
        ),
        Document(
            page_content="Toys come alive and have a blast doing so",
            metadata={"year": 1995, "genre": "animated"},
        ),
        Document(
            page_content="Three men walk into the Zone, three men walk out of the Zone",
            metadata={
                "year": 1979,
                "director": "Andrei Tarkovsky",
                "genre": "thriller",
                "rating": 9.9,
            },
        ),
    ]


def section_self_query() -> None:
    banner("3. SELF-QUERY RETRIEVER (movies + metadata filters)")
    docs = movie_docs()
    vectordb = fresh_chroma("movies", docs)

    metadata_field_info = [
        AttributeInfo(
            name="genre",
            description="The genre of the movie. One of ['science fiction', 'comedy', 'drama', 'thriller', 'romance', 'action', 'animated']",
            type="string",
        ),
        AttributeInfo(
            name="year",
            description="The year the movie was released",
            type="integer",
        ),
        AttributeInfo(
            name="director",
            description="The name of the movie director",
            type="string",
        ),
        AttributeInfo(
            name="rating",
            description="A 1-10 rating for the movie",
            type="float",
        ),
    ]
    document_content_description = "Brief summary of a movie."

    try:
        retriever = SelfQueryRetriever.from_llm(
            llm,
            vectordb,
            document_content_description,
            metadata_field_info,
        )
    except Exception as e:
        print(f"Could not build SelfQueryRetriever: {e}")
        return

    queries = [
        "I want to watch a movie rated higher than 8.5",
        "Has Greta Gerwig directed any movies about women",
        "What's a highly rated (above 8.5) science fiction film?",
        "I want to watch a movie directed by Christopher Nolan",
    ]
    for q in queries:
        print(f"Query: {q}")
        try:
            show_docs(retriever.invoke(q))
        except Exception as e:
            print(f"Soft-fail (re-run or simplify query): {e}\n")


def section_parent_document(txt_data) -> None:
    banner("4. PARENT DOCUMENT RETRIEVER (policies)")
    parent_splitter = CharacterTextSplitter(
        chunk_size=1000, chunk_overlap=20, separator="\n"
    )
    child_splitter = CharacterTextSplitter(
        chunk_size=200, chunk_overlap=20, separator="\n"
    )
    vectordb = fresh_chroma("split_parents")
    store = InMemoryStore()
    retriever = ParentDocumentRetriever(
        vectorstore=vectordb,
        docstore=store,
        child_splitter=child_splitter,
        parent_splitter=parent_splitter,
    )
    retriever.add_documents(txt_data)
    print(f"Parent keys in store: {len(list(store.yield_keys()))}")

    query = "smoking policy"
    sub_docs = vectordb.similarity_search(query)
    print(f"\nChild hit for '{query}':")
    print((sub_docs[0].page_content if sub_docs else "(none)")[:200])

    retrieved = retriever.invoke(query)
    print(f"\nParent return for '{query}':")
    print((retrieved[0].page_content if retrieved else "(none)")[:400])
    print()


def section_plain_policy_compare(chunks_txt) -> None:
    banner("5. PLAIN k=2 BASELINE (smoking policy)")
    vectordb = fresh_chroma("policies_k2", chunks_txt)
    docs = vectordb.as_retriever(search_kwargs={"k": 2}).invoke("smoking policy")
    show_docs(docs)


def main() -> None:
    policies_path = DATA / "companypolicies.txt"
    pdf_path = DATA / "langchain-paper.pdf"
    if not policies_path.exists() or not pdf_path.exists():
        raise FileNotFoundError("Missing data files — run download_data.py first")

    txt_data = TextLoader(str(policies_path)).load()
    chunks_txt = text_splitter(txt_data, 200, 20)
    print(f"Loaded policies → {len(chunks_txt)} chunks")

    pdf_data = PyPDFLoader(str(pdf_path)).load()
    chunks_pdf = text_splitter(pdf_data, 500, 20)
    print(f"Loaded PDF ({len(pdf_data)} pages) → {len(chunks_pdf)} chunks")

    section_basic_retrievers(chunks_txt)
    section_multiquery(chunks_pdf)
    section_self_query()
    section_parent_document(txt_data)
    section_plain_policy_compare(chunks_txt)
    print("Done.")


if __name__ == "__main__":
    main()
