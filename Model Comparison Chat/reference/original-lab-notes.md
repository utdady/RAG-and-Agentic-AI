# Original lab notes — Choosing the Right Model

Source: IBM Skills Network-style lab  
("Choosing the Right Model for Your Application").

Working app: [`../app.py`](../app.py) (Groq/Ollama, not Watsonx).

---

## How LLMs work (course summary)

1. **Tokenization** — text → tokens (e.g. BPE); try tools like Tiktokenizer  
2. **Embeddings** — tokens → vectors; similar meanings cluster  
3. **Attention** — each token attends to others (Transformer)  
4. **Layers** — stacked attention + residual paths  
5. **Next-token prediction** — training objective  
6. **Scale** — huge corpora + many parameters  
7. **Inference** — generate one token at a time; temperature/sampling trade off creativity vs consistency  

## How to choose a model

- **Capabilities** (text-only vs multimodal)  
- **Cost** (input/output tokens)  
- **Speed** (latency for real-time apps)  
- **Quality** (task-specific accuracy)  
- **Other** (vendor, license, integrations)  

Hands-on testing beats reading specs alone — this app’s model dropdown + `duration` supports that.

## Watsonx pieces (original)

```python
# Simple generate
ModelInference(model_id="ibm/granite-4-h-small", ...)

# ChatWatsonx + family-specific prompt templates
LLAMA_MODEL_ID = "meta-llama/llama-3-2-11b-vision-instruct"
GRANITE_MODEL_ID = "ibm/granite-4-h-small"
MISTRAL_MODEL_ID = "mistralai/mistral-small-3-1-24b-instruct-2503"
```

Prompt special tokens (lab):

- **Llama**: `<|begin_of_text|>`, roles in `<|start_header_id|>…`, `<|eot_id|>`  
- **Mistral**: `<s>`, `[INST]…[/INST]`  
- **Granite**: `<|system|>`, `<|user|>`, `<|assistant|>`  

Runnable port uses a **shared chat prompt + JSON schema** so one template works across Groq/Ollama models.

## Flask app (original)

- `GET /` → chat UI  
- `POST /generate` → `{ message, model }` → structured JSON + duration  
- Static assets from course gists (`script.js`, `styles.css`)  

JSON schema:

```json
{
  "summary": "...",
  "sentiment": 0-100,
  "response": "..."
}
```

## Setup (original Cloud IDE)

```bash
mkdir genai_flask_app && cd genai_flask_app
python3.11 -m venv venv && source venv/bin/activate
pip install ibm-watsonx-ai Flask langchain-ibm langchain
```
