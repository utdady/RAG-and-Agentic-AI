# Original lab notes (reference)

Source: IBM Skills Network–style lab — **AI Nutrition Coach** (Flask + Watsonx vision).

**Not the runnable app.** Runnable: `app.py` with Groq/Ollama vision.

---

## Course stack

- Flask + Jinja `index.html` + `style.css`
- Watsonx `ModelInference` multimodal `chat` with base64 `image_url`
- Nutritionist system prompt (ID → portions/calories → totals → nutrients → health eval → disclaimer)
- HTML formatting of `**bold**` and `*` bullets

## Pivot

| Course | Here |
|--------|------|
| Watsonx Llama vision | Groq vision / Ollama LLaVA |
| `debug=True` | `127.0.0.1:5002`, debug off |
| Skills Network credentials | Repo-root `.env` |
