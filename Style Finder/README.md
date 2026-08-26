# Style Finder

Gradio fashion **catalog matcher**: upload an outfit → ResNet50 embedding → cosine similarity against the course pickle → vision LLM style write-up (Groq / Ollama).

Course: IBM “Swift Style” / Style Finder lab (Watsonx Llama vision → **Groq vision / Ollama LLaVA**).

## Setup

```powershell
cd "Style Finder"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Secrets: repo-root [`.env`](../.env) (`GROQ_API_KEY`, optional `GROQ_VISION_MODEL` / `OLLAMA_VISION_MODEL`).

## Run

```powershell
python download_data.py   # once — ~fashion embeddings pickle
python app.py
```

Open http://127.0.0.1:7873

## Pipeline

1. Encode upload with ResNet50 (same forward path as the course embeddings)
2. Cosine match vs `data/swift-style-embeddings.pkl`
3. Collect catalog rows for the matched image URL
4. Vision LLM fashion analysis + item list (threshold from `SIMILARITY_THRESHOLD`)

Shopping “alternatives” APIs from the full lab starter are not required; catalog links from the pickle are shown in the UI.

## Reference

[`reference/original-lab-notes.md`](reference/original-lab-notes.md)
