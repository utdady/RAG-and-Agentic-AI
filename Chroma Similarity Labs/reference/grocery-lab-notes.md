# Original lab notes — Grocery text similarity

Source: "Similarity Search on Text Using Chroma DB and Python".

Working script: [`../grocery_lab.py`](../grocery_lab.py).

## Install

```bash
pip install chromadb==1.0.12
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install sentence-transformers==4.1.0
```

## Core idea

1. Create collection with MiniLM + cosine  
2. Add grocery strings (`fresh red apples`, …)  
3. Query `"apple"` (top 3)  
4. Batch query `["red", "fresh"]`  

Lab used Chroma 1.x `configuration={"hnsw": ..., "embedding_function": ef}`.  
Runnable port uses portable `embedding_function=` via `chroma_utils.create_collection`.

## Sample grocery texts

```text
fresh red apples, organic bananas, ripe mangoes, whole wheat bread,
farm-fresh eggs, natural yogurt, frozen vegetables, grass-fed beef,
free-range chicken, fresh salmon fillet, aromatic coffee beans,
pure honey, golden apple, red fruit
```
