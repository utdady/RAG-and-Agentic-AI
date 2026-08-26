# Original lab notes (reference)

Source: IBM Skills Network-style notebook  
("Explore Advanced Retrievers in LlamaIndex").

**Not the runnable lab** — uses Watsonx via `llama-index-llms-ibm`.  
Working script: [`../lab.py`](../lab.py) (Groq/Ollama via `shared.llama_index_llm`).

---

## Install (lab pins)

```bash
pip install llama-index==0.12.49 \
  llama-index-embeddings-huggingface==0.5.5 \
  llama-index-llms-ibm==0.4.0 \
  llama-index-retrievers-bm25==0.5.2 \
  sentence-transformers==5.0.0 \
  rank-bm25==0.2.2 \
  PyStemmer==2.2.0.3 \
  ibm-watsonx-ai==1.3.31
```

---

## Watsonx LLM setup (original)

```python
from ibm_watsonx_ai import APIClient
from llama_index.llms.ibm import WatsonxLLM
from llama_index.core.llms.mock import MockLLM

def create_watsonx_llm():
    try:
        api_client = APIClient({"url": "https://us-south.ml.cloud.ibm.com"})
        llm = WatsonxLLM(
            model_id="ibm/granite-4-h-small",
            url="https://us-south.ml.cloud.ibm.com",
            project_id="skills-network",
            api_client=api_client,
            temperature=0.9,
        )
        return llm
    except Exception as e:
        print(f"watsonx error: {e}; using MockLLM")
        return MockLLM(max_tokens=512)
```

---

## Embeddings + Settings

```python
from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
llm = create_watsonx_llm()
Settings.llm = llm
Settings.embed_model = embed_model
```

---

## Sample corpus + queries

Ten short AI/ML sentences (`SAMPLE_DOCUMENTS`) and a `DEMO_QUERIES` dict  
(`basic`, `technical`, `learning_types`, `advanced`, `applications`, `comprehensive`, `specific`).

---

## Lab class

```python
class AdvancedRetrieversLab:
    def __init__(self):
        self.documents = [Document(text=t) for t in SAMPLE_DOCUMENTS]
        self.nodes = SentenceSplitter().get_nodes_from_documents(self.documents)
        self.vector_index = VectorStoreIndex.from_documents(self.documents)
        self.document_summary_index = DocumentSummaryIndex.from_documents(self.documents)
        self.keyword_index = KeywordTableIndex.from_documents(self.documents)
```

---

## Retrievers covered

| # | Retriever | Notes |
|---|-----------|--------|
| 1 | `VectorIndexRetriever` | Dense similarity |
| 2 | `BM25Retriever` | Sparse; needs PyStemmer |
| 3 | Doc summary LLM / embedding | Needs LLM at index build |
| 4 | `AutoMergingRetriever` | `HierarchicalNodeParser` |
| 5 | `RecursiveRetriever` | Demo refs; often soft-fails |
| 6 | `QueryFusionRetriever` | `reciprocal_rerank`, `relative_score`, `dist_based_score` |
| 7 | Hybrid | `0.7 * vector + 0.3 * BM25` |
| 8 | `ProductionRAGPipeline` | Simple route + `llm.complete` |

### Vector

```python
vector_retriever = VectorIndexRetriever(index=lab.vector_index, similarity_top_k=3)
nodes = vector_retriever.retrieve(DEMO_QUERIES["basic"])
```

### BM25

```python
import Stemmer
from llama_index.retrievers.bm25 import BM25Retriever

bm25_retriever = BM25Retriever.from_defaults(
    nodes=lab.nodes,
    similarity_top_k=3,
    stemmer=Stemmer.Stemmer("english"),
    language="english",
)
```

### Query fusion (example)

```python
rrf_query_fusion = QueryFusionRetriever(
    [base_retriever],
    similarity_top_k=3,
    num_queries=3,
    mode="reciprocal_rerank",
    use_async=False,
    verbose=True,
)
```

### Hybrid score

```python
hybrid_score = 0.7 * vector_score + 0.3 * bm25_score
```

---

## Fusion mode cheat sheet (from lab)

- **RRF** — production stability, rank-based  
- **Relative score** — preserves confidence / interpretability  
- **Distribution-based** — statistical robustness (scipy helps)

Full narrative and manual RRF/relative/dist math demos lived in the notebook cells;  
the runnable port consolidates them in `lab.py` with soft-fail fallbacks.
