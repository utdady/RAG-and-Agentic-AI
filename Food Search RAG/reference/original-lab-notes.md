# Original lab notes (reference)

Source: IBM Skills Network-style lab  
("Interactive Food Search and RAG Chatbot System").

**Not the runnable package** — RAG stage used Watsonx Granite.  
Working code: `../shared_food.py` + CLIs under `../` (Groq/Ollama for chat).

---

## Install / data

```bash
pip install numpy==2.3.1 scipy==1.16.0 chromadb==1.0.12 \
  sentence-transformers==4.1.0 ibm-watsonx-ai==1.3.24

wget https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/sN1PIR8qp1SJ6K7syv72qQ/FoodDataSet.json
```

Sample food record shape:

```json
{
  "food_id": 1,
  "food_name": "Apple Pie",
  "food_description": "...",
  "food_calories_per_serving": 320,
  "food_nutritional_factors": {"carbohydrates": "42g", "protein": "2g", "fat": "16g"},
  "food_ingredients": ["Apples", "Flour", "Butter", "Sugar", "Cinnamon", "Nutmeg"],
  "food_health_benefits": "Rich in antioxidants and dietary fiber",
  "cooking_method": "Baking",
  "cuisine_type": "American",
  "food_features": {
    "taste": "sweet",
    "texture": "crisp and tender",
    "appearance": "golden brown",
    "preparation": "baked",
    "serving_type": "hot"
  }
}
```

---

## Shared helpers (`shared_functions` in the lab)

- `load_food_data` — normalize ids, ingredients, `taste_profile` from `food_features`
- `create_similarity_search_collection` — Chroma + `SentenceTransformerEmbeddingFunction("all-MiniLM-L6-v2")`
- `populate_similarity_collection` — rich document text + metadata
- `perform_similarity_search` / `perform_filtered_similarity_search` — cuisine + `$lte` calories

Lab used Chroma 1.x:

```python
client.create_collection(
    name=collection_name,
    metadata=collection_metadata,
    configuration={
        "hnsw": {"space": "cosine"},
        "embedding_function": sentence_transformer_ef,
    },
)
```

Runnable port uses portable `embedding_function=` + `metadata={"hnsw:space": "cosine"}`.

---

## Scripts in the original lab

| File | Role |
|------|------|
| `interactive_search.py` | CLI search (+ later `history`) |
| `advanced_search.py` | Cuisine / calorie / combined / demos |
| `rag_chatbot.py` | Retrieve + IBM Granite `model.generate` |
| `comparison.py` | Timing of three approaches (RAG side was templated) |
| `calorie_checker.py` | Budget filter practice |
| `result_limiter.py` | Vary `n_results` |

### Watsonx RAG init (original)

```python
from ibm_watsonx_ai.foundation_models import ModelInference

model = ModelInference(
    model_id="ibm/granite-4-h-small",
    credentials={"url": "https://us-south.ml.cloud.ibm.com"},
    params={"max_new_tokens": 400},
    project_id="skills-network",
)
```

Runnable `rag_chat.py` uses `shared.llm.get_llm_info()` instead, with the same retrieve → prompt → answer flow and fallbacks.
