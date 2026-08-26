# Original lab notes (reference)

Source: IBM Skills Network-style notebook  
("Build a Smarter Search with LangChain Context Retrieval").

**Not the runnable lab** — uses Watsonx LLM + Watsonx embeddings.  
Working script: [`../lab.py`](../lab.py) (Groq/Ollama + local MiniLM + Chroma).

---

## Install (lab pins)

```bash
pip install "ibm-watsonx-ai==1.1.2"
pip install "langchain==0.2.1"
pip install "langchain-ibm==0.1.11"
pip install "langchain-community==0.2.1"
pip install "chromadb==0.4.24"
pip install "pypdf==4.3.1"
pip install "lark==1.1.9"
pip install 'posthog<6.0.0'
```

---

## Watsonx LLM + embeddings (original)

```python
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from ibm_watsonx_ai.foundation_models.extensions.langchain import WatsonxLLM
from ibm_watsonx_ai.metanames import EmbedTextParamsMetaNames
from langchain_ibm import WatsonxEmbeddings

def llm():
    model = ModelInference(
        model_id="mistralai/mistral-small-3-1-24b-instruct-2503",
        params={
            GenParams.MAX_NEW_TOKENS: 256,
            GenParams.TEMPERATURE: 0.5,
        },
        credentials={"url": "https://us-south.ml.cloud.ibm.com"},
        project_id="skills-network",
    )
    return WatsonxLLM(model=model)


def watsonx_embedding():
    return WatsonxEmbeddings(
        model_id="mistralai/mistral-small-3-1-24b-instruct-2503",
        url="https://us-south.ml.cloud.ibm.com",
        project_id="skills-network",
        params={
            EmbedTextParamsMetaNames.TRUNCATE_INPUT_TOKENS: 3,
            EmbedTextParamsMetaNames.RETURN_OPTIONS: {"input_text": True},
        },
    )
```

Note: `TRUNCATE_INPUT_TOKENS: 3` looks like a lab typo; the runnable port uses full local MiniLM embeddings.

---

## Text split helper

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

def text_splitter(data, chunk_size, chunk_overlap):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    return splitter.split_documents(data)
```

---

## Assets

```bash
wget "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/MZ9z1lm-Ui3YBp3SYWLTAQ/companypolicies.txt"
```

PDF via `PyPDFLoader` URL:

`https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/ioch1wsxkfqgfLLgmd-6Rw/langchain-paper.pdf`

(Windows: use `download_data.py` instead of `wget`.)

---

## Basic Chroma retrievers

```python
from langchain.vectorstores import Chroma

vectordb = Chroma.from_documents(chunks_txt, watsonx_embedding())
query = "email policy"

vectordb.as_retriever().invoke(query)
vectordb.as_retriever(search_kwargs={"k": 1}).invoke(query)
vectordb.as_retriever(search_type="mmr").invoke(query)
vectordb.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={"score_threshold": 0.4},
).invoke(query)
```

---

## MultiQuery (paper)

```python
from langchain.retrievers.multi_query import MultiQueryRetriever

retriever = MultiQueryRetriever.from_llm(
    retriever=vectordb.as_retriever(),
    llm=llm(),
)
retriever.invoke("What does the paper say about langchain?")
```

---

## SelfQuery (movies)

Uses `AttributeInfo` for `genre`, `year`, `director`, `rating` and example queries such as:

- "I want to watch a movie rated higher than 8.5"
- "Has Greta Gerwig directed any movies about women"
- "What's a highly rated (above 8.5) science fiction film?"
- "I want to watch a movie directed by Christopher Nolan"

The notebook’s final block rebuilt a SelfQuery store from policy smoking-policy hits — that was a paste error and is **omitted** in `lab.py`.

---

## ParentDocumentRetriever

```python
from langchain.retrievers import ParentDocumentRetriever
from langchain.storage import InMemoryStore
from langchain_text_splitters import CharacterTextSplitter

parent_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=20, separator="\n")
child_splitter = CharacterTextSplitter(chunk_size=200, chunk_overlap=20, separator="\n")

vectordb = Chroma(collection_name="split_parents", embedding_function=watsonx_embedding())
store = InMemoryStore()
retriever = ParentDocumentRetriever(
    vectorstore=vectordb,
    docstore=store,
    child_splitter=child_splitter,
    parent_splitter=parent_splitter,
)
retriever.add_documents(txt_data)
```

Compare child `similarity_search("smoking policy")` vs parent `retriever.invoke("smoking policy")`.
