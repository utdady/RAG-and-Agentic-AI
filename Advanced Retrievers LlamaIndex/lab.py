"""
Explore Advanced Retrievers in LlamaIndex
Vector / BM25 / doc-summary / auto-merge / recursive / query fusion / hybrid / mini pipeline

LLM: Groq or Ollama via shared.llama_index_llm (not Watsonx).
Embeddings: local BAAI/bge-small-en-v1.5
"""

from __future__ import annotations

import os
import sys
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shared.env_load import load_env

load_env(Path(__file__).resolve().parent)
from llama_index.core import (
    Document,
    DocumentSummaryIndex,
    KeywordTableIndex,
    Settings,
    StorageContext,
    VectorStoreIndex,
)
from llama_index.core.node_parser import HierarchicalNodeParser, SentenceSplitter
from llama_index.core.retrievers import (
    AutoMergingRetriever,
    QueryFusionRetriever,
    RecursiveRetriever,
    VectorIndexRetriever,
)
from llama_index.core.storage.docstore import SimpleDocumentStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.retrievers.bm25 import BM25Retriever

from shared.env_load import load_env
from shared.llama_index_llm import describe_llama_index_llm, get_llama_index_llm

try:
    from scipy import stats  # noqa: F401

    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False

SAMPLE_DOCUMENTS = [
    "Machine learning is a subset of artificial intelligence that focuses on algorithms that can learn from data.",
    "Deep learning uses neural networks with multiple layers to model and understand complex patterns in data.",
    "Natural language processing enables computers to understand, interpret, and generate human language.",
    "Computer vision allows machines to interpret and understand visual information from the world.",
    "Reinforcement learning is a type of machine learning where agents learn to make decisions through rewards and penalties.",
    "Supervised learning uses labeled training data to learn a mapping from inputs to outputs.",
    "Unsupervised learning finds hidden patterns in data without labeled examples.",
    "Transfer learning leverages knowledge from pre-trained models to improve performance on new tasks.",
    "Generative AI can create new content including text, images, code, and more.",
    "Large language models are trained on vast amounts of text data to understand and generate human-like text.",
]

DEMO_QUERIES = {
    "basic": "What is machine learning?",
    "technical": "neural networks deep learning",
    "learning_types": "different types of learning",
    "advanced": "How do neural networks work in deep learning?",
    "applications": "What are the applications of AI?",
    "comprehensive": "What are the main approaches to machine learning?",
    "specific": "supervised learning techniques",
}


def _banner(title: str) -> None:
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def _print_nodes(nodes, limit: int = 3) -> None:
    for i, node in enumerate(nodes[:limit], 1):
        score = getattr(node, "score", None)
        score_s = f"{score:.4f}" if isinstance(score, (int, float)) else "n/a"
        text = (node.text or "")[:100]
        print(f"{i}. Score: {score_s}")
        print(f"   Text: {text}...")
        print()


class AdvancedRetrieversLab:
    def __init__(self, llm, build_summary_index: bool = True):
        print("Initializing Advanced Retrievers Lab...")
        self.documents = [Document(text=text) for text in SAMPLE_DOCUMENTS]
        self.nodes = SentenceSplitter().get_nodes_from_documents(self.documents)

        print("Creating indexes...")
        self.vector_index = VectorStoreIndex.from_documents(self.documents)
        self.keyword_index = KeywordTableIndex.from_documents(self.documents)

        self.document_summary_index = None
        if build_summary_index:
            try:
                print("Building DocumentSummaryIndex (LLM calls)...")
                self.document_summary_index = DocumentSummaryIndex.from_documents(
                    self.documents
                )
            except Exception as e:
                print(f"DocumentSummaryIndex skipped: {e}")

        print(
            f"Ready — {len(self.documents)} docs, {len(self.nodes)} nodes"
        )


def section_vector(lab: AdvancedRetrieversLab) -> None:
    _banner("1. VECTOR INDEX RETRIEVER")
    retriever = VectorIndexRetriever(index=lab.vector_index, similarity_top_k=3)
    query = DEMO_QUERIES["basic"]
    nodes = retriever.retrieve(query)
    print(f"Query: {query}")
    print(f"Retrieved {len(nodes)} nodes:")
    _print_nodes(nodes)


def section_bm25(lab: AdvancedRetrieversLab) -> None:
    _banner("2. BM25 RETRIEVER")
    query = DEMO_QUERIES["technical"]
    try:
        import Stemmer

        bm25 = BM25Retriever.from_defaults(
            nodes=lab.nodes,
            similarity_top_k=3,
            stemmer=Stemmer.Stemmer("english"),
            language="english",
        )
        nodes = bm25.retrieve(query)
        print(f"Query: {query}")
        print("BM25 = keyword scoring with term saturation + length norm")
        for i, node in enumerate(nodes, 1):
            score = node.score if getattr(node, "score", None) is not None else 0
            print(f"{i}. BM25 Score: {score:.4f}")
            print(f"   Text: {node.text[:100]}...")
            found = [t for t in query.lower().split() if t in node.text.lower()]
            if found:
                print(f"   → Found terms: {found}")
            print()
    except Exception as e:
        print(f"BM25 unavailable ({e}); vector fallback")
        nodes = lab.vector_index.as_retriever(similarity_top_k=3).retrieve(query)
        _print_nodes(nodes)


def section_doc_summary(lab: AdvancedRetrieversLab) -> None:
    _banner("3. DOCUMENT SUMMARY INDEX RETRIEVERS")
    if lab.document_summary_index is None:
        print("Skipped — DocumentSummaryIndex was not built.")
        return

    from llama_index.core.indices.document_summary import (
        DocumentSummaryIndexEmbeddingRetriever,
        DocumentSummaryIndexLLMRetriever,
    )

    query = DEMO_QUERIES["learning_types"]
    print(f"Query: {query}")

    print("\nA) LLM-based summary retriever")
    try:
        r = DocumentSummaryIndexLLMRetriever(
            lab.document_summary_index, choice_top_k=3
        )
        _print_nodes(r.retrieve(query), limit=2)
    except Exception as e:
        print(f"  Soft-fail: {e}")

    print("B) Embedding-based summary retriever")
    try:
        r = DocumentSummaryIndexEmbeddingRetriever(
            lab.document_summary_index, similarity_top_k=3
        )
        _print_nodes(r.retrieve(query), limit=2)
    except Exception as e:
        print(f"  Soft-fail: {e}")


def section_auto_merge(lab: AdvancedRetrieversLab) -> None:
    _banner("4. AUTO MERGING RETRIEVER")
    node_parser = HierarchicalNodeParser.from_defaults(chunk_sizes=[512, 256, 128])
    hier_nodes = node_parser.get_nodes_from_documents(lab.documents)
    docstore = SimpleDocumentStore()
    docstore.add_documents(hier_nodes)
    storage_context = StorageContext.from_defaults(docstore=docstore)
    base_index = VectorStoreIndex(hier_nodes, storage_context=storage_context)
    base_retriever = base_index.as_retriever(similarity_top_k=6)
    auto_merging = AutoMergingRetriever(base_retriever, storage_context, verbose=True)

    query = DEMO_QUERIES["advanced"]
    nodes = auto_merging.retrieve(query)
    print(f"Query: {query}")
    print(f"Auto-merged to {len(nodes)} nodes")
    _print_nodes(nodes)


def section_recursive(lab: AdvancedRetrieversLab) -> None:
    _banner("5. RECURSIVE RETRIEVER")
    docs_with_refs = []
    for i, doc in enumerate(lab.documents):
        docs_with_refs.append(
            Document(
                text=doc.text,
                metadata={
                    "doc_id": f"doc_{i}",
                    "references": [
                        f"doc_{j}" for j in range(len(lab.documents)) if j != i
                    ][:2],
                },
            )
        )
    ref_index = VectorStoreIndex.from_documents(docs_with_refs)
    base_retriever = ref_index.as_retriever(similarity_top_k=2)
    retriever_dict = {
        f"doc_{i}": ref_index.as_retriever(similarity_top_k=1)
        for i in range(len(docs_with_refs))
    }
    retriever_dict["vector"] = base_retriever

    recursive = RecursiveRetriever(
        "vector",
        retriever_dict=retriever_dict,
        query_engine_dict={},
        verbose=True,
    )
    query = DEMO_QUERIES["applications"]
    try:
        nodes = recursive.retrieve(query)
        print(f"Query: {query}")
        print(f"Recursively retrieved {len(nodes)} nodes")
        _print_nodes(nodes)
    except Exception as e:
        print(f"Query: {query}")
        print(f"Recursive soft-fail ({e}); basic fallback")
        _print_nodes(base_retriever.retrieve(query), limit=2)


def section_query_fusion(lab: AdvancedRetrieversLab) -> None:
    _banner("6. QUERY FUSION RETRIEVER")
    query = DEMO_QUERIES["comprehensive"]
    base = lab.vector_index.as_retriever(similarity_top_k=5)
    modes = [
        ("reciprocal_rerank", "RRF — rank-based, robust"),
        ("relative_score", "Relative — normalize by max score"),
        ("dist_based_score", "Distribution — statistical norm"),
    ]
    print(f"Query: {query}")
    for mode, blurb in modes:
        print(f"\n--- mode={mode} ({blurb}) ---")
        try:
            fusion = QueryFusionRetriever(
                [base],
                similarity_top_k=3,
                num_queries=3,
                mode=mode,
                use_async=False,
                verbose=False,
            )
            _print_nodes(fusion.retrieve(query))
        except Exception as e:
            print(f"Soft-fail: {e}")
            print("Manual RRF fallback with fixed query variants...")
            _manual_rrf(base, query)


def _manual_rrf(base_retriever, query: str) -> None:
    variants = [
        query,
        "machine learning approaches and methods",
        "different ML techniques and algorithms",
    ]
    all_results: dict = {}
    for qi, qv in enumerate(variants):
        for rank, node in enumerate(base_retriever.retrieve(qv)):
            nid = node.node.node_id
            entry = all_results.setdefault(
                nid, {"node": node, "rrf_score": 0.0}
            )
            entry["rrf_score"] += 1.0 / (rank + 1 + 60)
    ranked = sorted(all_results.values(), key=lambda x: x["rrf_score"], reverse=True)
    for i, result in enumerate(ranked[:3], 1):
        print(f"{i}. RRF Score: {result['rrf_score']:.4f}")
        print(f"   Text: {result['node'].text[:100]}...")
        print()


def section_hybrid(lab: AdvancedRetrieversLab) -> None:
    _banner("7. HYBRID RETRIEVE (vector 0.7 + BM25 0.3)")
    vector_retriever = lab.vector_index.as_retriever(similarity_top_k=10)
    try:
        bm25_retriever = BM25Retriever.from_defaults(
            nodes=lab.nodes, similarity_top_k=10
        )
    except Exception:
        bm25_retriever = vector_retriever

    def hybrid_retrieve(query: str, top_k: int = 3):
        vector_results = vector_retriever.retrieve(query)
        bm25_results = bm25_retriever.retrieve(query)
        vector_scores, bm25_scores, all_nodes = {}, {}, {}

        max_v = max((r.score or 0) for r in vector_results) or 1
        for r in vector_results:
            key = r.text.strip()
            vector_scores[key] = (r.score or 0) / max_v
            all_nodes[key] = r

        max_b = max((r.score or 0) for r in bm25_results) or 1
        for r in bm25_results:
            key = r.text.strip()
            bm25_scores[key] = (r.score or 0) / max_b
            all_nodes[key] = r

        hybrid = []
        for key, node in all_nodes.items():
            v, b = vector_scores.get(key, 0), bm25_scores.get(key, 0)
            hybrid.append(
                {
                    "node": node,
                    "vector_score": v,
                    "bm25_score": b,
                    "hybrid_score": 0.7 * v + 0.3 * b,
                }
            )
        hybrid.sort(key=lambda x: x["hybrid_score"], reverse=True)
        return hybrid[:top_k]

    for query in [
        DEMO_QUERIES["basic"],
        DEMO_QUERIES["technical"],
        DEMO_QUERIES["specific"],
    ]:
        print(f"Query: {query}")
        for i, result in enumerate(hybrid_retrieve(query), 1):
            print(f"{i}. Hybrid: {result['hybrid_score']:.3f} "
                  f"(V={result['vector_score']:.3f}, B={result['bm25_score']:.3f})")
            print(f"   Text: {result['node'].text[:80]}...")
        print()


def section_pipeline(lab: AdvancedRetrieversLab, llm) -> None:
    _banner("8. MINI PRODUCTION RAG PIPELINE")

    class ProductionRAGPipeline:
        def __init__(self, index, llm):
            self.llm = llm
            self.vector_retriever = index.as_retriever(similarity_top_k=5)

        def _route_query(self, question: str) -> str:
            q = question.lower()
            if any(w in q for w in ("list", "types", "examples")):
                return "comprehensive"
            return "semantic"

        def query(self, question: str, strategy: str = "auto"):
            if strategy == "auto":
                strategy = self._route_query(question)
            top_k = 5 if strategy == "comprehensive" else 3
            docs = self.vector_retriever.retrieve(question)
            context = "\n\n".join(d.text for d in docs[:top_k])
            prompt = (
                f"Based on the following context, answer the question.\n\n"
                f"Context:\n{context}\n\nQuestion: {question}\n\nAnswer:"
            )
            try:
                response = self.llm.complete(prompt)
                return {
                    "answer": response.text,
                    "strategy": strategy,
                    "num_docs": len(docs),
                    "status": "success",
                }
            except Exception as e:
                return {
                    "answer": context[:200] + "...",
                    "strategy": strategy,
                    "num_docs": len(docs),
                    "status": f"llm_error: {e}",
                }

    pipeline = ProductionRAGPipeline(lab.vector_index, llm)
    for query in [
        "What is machine learning?",
        "List different types of learning algorithms",
        "Explain neural networks",
    ]:
        result = pipeline.query(query)
        print(f"\nQuery: {query}")
        print(f"Strategy: {result['strategy']} | Status: {result['status']}")
        print(f"Answer: {result['answer'][:160]}...")


def main() -> None:
    print(describe_llama_index_llm())
    if not SCIPY_AVAILABLE:
        print("scipy not installed — dist-based fusion may be limited")

    embed_name = os.getenv("LLAMA_EMBED_MODEL", "BAAI/bge-small-en-v1.5")
    print(f"Embeddings={embed_name}")
    embed_model = HuggingFaceEmbedding(model_name=embed_name)
    llm = get_llama_index_llm(temperature=0.3)
    Settings.llm = llm
    Settings.embed_model = embed_model

    skip_summary = os.getenv("SKIP_DOC_SUMMARY", "false").lower() == "true"
    lab = AdvancedRetrieversLab(llm, build_summary_index=not skip_summary)

    section_vector(lab)
    section_bm25(lab)
    section_doc_summary(lab)
    section_auto_merge(lab)
    section_recursive(lab)
    section_query_fusion(lab)
    section_hybrid(lab)
    section_pipeline(lab, llm)
    print("\nDone.")


if __name__ == "__main__":
    main()
