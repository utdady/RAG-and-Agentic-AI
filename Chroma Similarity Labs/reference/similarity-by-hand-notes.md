# Original lab notes — Similarity search by hand

Source: "Similarity Search by Hand".

Working script: [`../similarity_by_hand.py`](../similarity_by_hand.py).

## Install

```bash
pip install sentence-transformers==4.1.0
# also needs numpy, scipy, torch
```

## Corpus

Four sentences that all contain "Bugs" but mean software bugs vs insects — so embeddings must disambiguate by context.

## Exercises covered

1. Encode with `paraphrase-MiniLM-L6-v2`
2. Manual Euclidean distance + full matrix; upper-triangle optimization
3. Compare to `scipy.spatial.distance.cdist(..., 'euclidean')`
4. Manual dot product vs `embeddings @ embeddings.T` / `np.matmul` / `np.dot`
5. L2-normalize rows; verify unit length; compare to `torch.nn.functional.normalize`
6. Cosine similarity = dot of normalized vectors; cosine distance = `1 - sim`
7. Embed a query, normalize, argmax cosine → retrieve best document

Expected top hit for  
`"Who is responsible for a coding project and fixing others' mistakes?"`  
→ intern / lead developer sentence.
