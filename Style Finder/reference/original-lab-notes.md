# Original lab notes (reference)

Source: IBM Skills Network Style Finder / “swift-style” lab  
(starter: `ibm-developer-skills-network/tyxva-swift-style`, branch `1-start`).

**Not the runnable app** — Watsonx Llama vision preserved for comparison.  
Runnable app: `app.py` (Groq/Ollama vision + local ResNet50).

---

## Assets

```bash
git clone --no-checkout https://github.com/ibm-developer-skills-network/tyxva-swift-style.git style-finder
cd style-finder && git checkout 1-start
wget -O swift-style-embeddings.pkl \
  https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/95eJ0YJVtqTZhEd7RaUlew/processed-swift-style-with-embeddings.pkl
```

## Modules (course)

- `config.py` — Llama model id, image size, similarity threshold  
- `image_processor.py` — ResNet50 encode + cosine `find_closest_match`  
- `llm_service.py` / `LlamaVisionService` — Watsonx multimodal chat fashion prompts  
- `helpers.py` — related items by Image URL, format alternatives, process Markdown  

## Pivot

| Course | Here |
|--------|------|
| Watsonx Llama vision | Groq vision / Ollama LLaVA |
| `pretrained=True` | `ResNet50_Weights.DEFAULT` |
| External shopping alternatives | Catalog rows from pickle (links in UI) |
| Notebook / incomplete app paste | Gradio `app.py` on port 7873 |
