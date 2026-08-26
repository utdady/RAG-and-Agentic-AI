# Shared helpers

## LLM (`shared.llm`)

```python
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # adjust depth as needed
sys.path.insert(0, str(ROOT))

from shared.llm import get_chat_llm, get_llm_info, resolve_whisper_model, describe_setup

llm, info = get_llm_info(temperature=0.5)
print(describe_setup())  # e.g. LLM=groq:llama-3.1-8b-instant (tier=mid); Whisper=...
```

**Provider resolution**

| `LLM_PROVIDER` | Behavior |
|----------------|----------|
| `auto` (default) | Groq if `GROQ_API_KEY` set, else Ollama |
| `groq` | Require `GROQ_API_KEY` |
| `ollama` | Local; model from `OLLAMA_MODEL` or hardware tier |

**Ollama tiers** (when `OLLAMA_MODEL` unset): prefers an already-pulled model, else suggests `llama3.2:1b` / `llama3.2:3b` / `llama3.1:8b`.

Install: `pip install -r shared/requirements.txt`

Also see `shared/embeddings.py` for local HuggingFace embeddings used by FAISS/RAG apps,
and `shared/llama_index_llm.py` for Groq/Ollama under LlamaIndex (`get_llama_index_llm`).
