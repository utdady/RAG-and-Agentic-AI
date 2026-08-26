# Chroma Similarity Labs

Progressive similarity demos (no LLM / API key required).

| Order | Script | Focus |
|-------|--------|--------|
| 0 | `similarity_by_hand.py` | Euclidean, dot product, normalize, cosine — from scratch |
| 1 | `grocery_lab.py` | Chroma: add text, single + batch query |
| 2 | `employees_lab.py` | Metadata filters + combined query+filter |
| 3 | `books_lab.py` | Same patterns on a books corpus |

Shared helper: `chroma_utils.py` (portable collection create for labs 1–3).

## Setup

```powershell
cd "Chroma Similarity Labs"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Optional CPU torch wheel (Windows):

```powershell
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

## Run

```powershell
python similarity_by_hand.py   # start here (math under the hood)
python grocery_lab.py
python employees_lab.py
python books_lab.py
```

## Reference

Original course pastes: [`reference/`](reference/).
