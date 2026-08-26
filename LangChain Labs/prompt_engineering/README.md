# Prompt Engineering (LangChain Labs)

Master zero / one / few-shot prompting, CoT, and `PromptTemplate` + LCEL.

Sibling of [`../fundamentals/`](../fundamentals/) — deeper prompt craft, not another product UI.

**LLM:** Groq / Ollama via [`../../shared/llm.py`](../../shared/llm.py)

## Run

From repo setup in `LangChain Labs/` (same venv + `requirements.txt`):

```powershell
cd "LangChain Labs\prompt_engineering"
python 01_techniques.py
python 02_templates_lcel.py
python 03_review_analysis.py
```

| Script | Topic |
|--------|--------|
| `01_techniques.py` | Completions, zero/one/few-shot, CoT, self-consistency |
| `02_templates_lcel.py` | PromptTemplate chains: joke, summarize, QA, classify, SQL, roleplay |
| `03_review_analysis.py` | Structured product-review analysis |

## Notes

- Watsonx `max_new_tokens` / `top_p` / `top_k` → mainly **temperature** via `shared.llm`
- Prefer `prompt | llm | parser` over `RunnableLambda(format)` + legacy `LLMChain`
- Roleplay is a single demo turn (original used `input()` loop)

## Reference

[`reference/original-lab-notes.md`](reference/original-lab-notes.md)
