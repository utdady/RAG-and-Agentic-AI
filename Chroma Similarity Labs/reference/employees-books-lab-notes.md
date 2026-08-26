# Original lab notes — Employees & books

Sources:

- "Similarity Search on Employee Records using Python and Chroma DB"
- Books advanced search companion notebook

Working scripts: [`../employees_lab.py`](../employees_lab.py), [`../books_lab.py`](../books_lab.py).

## Install

```bash
pip install chromadb==1.0.12
pip install sentence-transformers==4.1.0
```

## Employees — demos

1. Similarity: "Python developer with web development experience"  
2. Similarity: "team leader manager with experience"  
3. Filter: `department == Engineering`  
4. Filter: `experience >= 10`  
5. Filter: `location in [San Francisco, Los Angeles]`  
6. Combined: semantic query + `experience >= 8` + tech-city `$in`

Documents are built from role, years, department, skills, location, employment type.

## Books — demos

1. Similarity: magical fantasy adventure  
2. Filter: genre in Fantasy / Science Fiction  
3. Filter: rating >= 4.3  
4. Combined: dystopian themes + rating >= 4.0  

## Note

Original pastes had stub `main()` / dead `return` / empty `perform_advanced_search`; the runnable labs fold everything into a clean `main()`.
