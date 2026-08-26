"""
Lab 0 — Similarity search by hand (no Chroma).

Euclidean distance, dot product, L2 normalization, cosine similarity,
then retrieve the best document for a query embedding.
"""

from __future__ import annotations

import math

import numpy as np
import scipy.spatial.distance
import torch
from sentence_transformers import SentenceTransformer

DOCUMENTS = [
    "Bugs introduced by the intern had to be squashed by the lead developer.",
    "Bugs found by the quality assurance engineer were difficult to debug.",
    "Bugs are common throughout the warm summer months, according to the entomologist.",
    "Bugs, in particular spiders, are extensively studied by arachnologists.",
]


def euclidean_distance_fn(vector1, vector2) -> float:
    squared_sum = sum((x - y) ** 2 for x, y in zip(vector1, vector2))
    return math.sqrt(squared_sum)


def dot_product_fn(vector1, vector2) -> float:
    return sum(x * y for x, y in zip(vector1, vector2))


def main() -> None:
    print("Loading paraphrase-MiniLM-L6-v2...")
    model = SentenceTransformer("paraphrase-MiniLM-L6-v2")
    embeddings = model.encode(DOCUMENTS)
    print(f"Embeddings shape: {embeddings.shape}")

    print("\n=== Euclidean (L2) distance ===")
    print(f"Manual d(0,1) = {euclidean_distance_fn(embeddings[0], embeddings[1]):.6f}")
    print(f"Manual d(1,0) = {euclidean_distance_fn(embeddings[1], embeddings[0]):.6f}")

    n = embeddings.shape[0]
    l2_dist_manual = np.zeros([n, n])
    for i in range(n):
        for j in range(n):
            l2_dist_manual[i, j] = euclidean_distance_fn(embeddings[i], embeddings[j])

    l2_dist_manual_improved = np.zeros([n, n])
    for i in range(n):
        for j in range(n):
            if j > i:
                l2_dist_manual_improved[i, j] = euclidean_distance_fn(
                    embeddings[i], embeddings[j]
                )
            elif i > j:
                l2_dist_manual_improved[i, j] = l2_dist_manual_improved[j, i]

    l2_dist_scipy = scipy.spatial.distance.cdist(embeddings, embeddings, "euclidean")
    print(f"Manual vs scipy allclose: {np.allclose(l2_dist_manual, l2_dist_scipy)}")
    print(f"Improved upper-triangle matrix:\n{np.round(l2_dist_manual_improved, 4)}")

    print("\n=== Dot product ===")
    print(f"Manual dot(0,1) = {dot_product_fn(embeddings[0], embeddings[1]):.6f}")
    dot_product_manual = np.empty([n, n])
    for i in range(n):
        for j in range(n):
            dot_product_manual[i, j] = dot_product_fn(embeddings[i], embeddings[j])

    dot_product_operator = embeddings @ embeddings.T
    print(
        "Manual vs @ operator allclose: "
        f"{np.allclose(dot_product_manual, dot_product_operator, atol=1e-5)}"
    )
    print(f"np.matmul close: {np.allclose(np.matmul(embeddings, embeddings.T), dot_product_operator)}")

    print("\n=== L2 normalize + cosine similarity ===")
    l2_norms = np.sqrt(np.sum(embeddings**2, axis=1)).reshape(-1, 1)
    normalized_manual = embeddings / l2_norms
    unit_lengths = np.sqrt(np.sum(normalized_manual**2, axis=1))
    print(f"Normalized vector lengths (~1): {np.round(unit_lengths, 3)}")

    normalized_torch = torch.nn.functional.normalize(
        torch.from_numpy(embeddings)
    ).numpy()
    print(
        f"Manual vs torch.normalize allclose: "
        f"{np.allclose(normalized_manual, normalized_torch)}"
    )

    cosine_manual = np.empty([n, n])
    for i in range(n):
        for j in range(n):
            cosine_manual[i, j] = dot_product_fn(
                normalized_manual[i], normalized_manual[j]
            )
    cosine_operator = normalized_manual @ normalized_manual.T
    print(f"Cosine manual vs @: {np.allclose(cosine_manual, cosine_operator)}")
    print(f"Cosine similarity matrix:\n{np.round(cosine_manual, 4)}")
    print(f"Cosine distance (1 - sim):\n{np.round(1 - cosine_manual, 4)}")

    print("\n=== Query retrieval ===")
    query = "Who is responsible for a coding project and fixing others' mistakes?"
    query_embedding = model.encode([query])
    normalized_query = torch.nn.functional.normalize(
        torch.from_numpy(query_embedding)
    ).numpy()
    scores = normalized_manual @ normalized_query.T
    best = int(scores.argmax())
    print(f"Query: {query}")
    print(f"Best match (index {best}, cos={float(scores[best]):.4f}):")
    print(f"  {DOCUMENTS[best]}")
    print("\nAll scores:")
    for i, doc in enumerate(DOCUMENTS):
        print(f"  [{i}] {float(scores[i]):.4f}  {doc[:70]}...")


if __name__ == "__main__":
    main()
