"""Dense retrieval: text -> tokens -> transformer -> pooled vector -> cosine.

Model: intfloat/multilingual-e5-small (118M params, 384-dim, supports Vietnamese).
E5 was trained with the prefixes "query: " and "passage: ", and leaving them
out measurably hurts retrieval, so we always add them.

With L2-normalised vectors, cosine similarity equals the dot product, so
cosine(q, d) = q . d. `cosine_top_k` does exactly that with numpy;
`FaissIndex` does the same exact search with FAISS IndexFlatIP, which is the
building block you would replace with an ANN index (IVF/HNSW) at scale.
"""

from __future__ import annotations

import logging
from collections import OrderedDict

import numpy as np

log = logging.getLogger(__name__)


def cosine_top_k(query_vec: np.ndarray, matrix: np.ndarray, k: int) -> list[tuple[int, float]]:
    """Plain-numpy exact search. Inputs must already be L2-normalised."""
    sims = matrix @ query_vec
    k = min(k, len(sims))
    top = np.argpartition(-sims, k - 1)[:k]
    top = top[np.argsort(-sims[top])]
    return [(int(i), float(sims[i])) for i in top]


class FaissIndex:
    def __init__(self, matrix: np.ndarray) -> None:
        import faiss  # imported lazily so unit tests do not need it

        self.index = faiss.IndexFlatIP(matrix.shape[1])
        self.index.add(matrix.astype(np.float32))

    def search(self, query_vec: np.ndarray, k: int) -> list[tuple[int, float]]:
        scores, ids = self.index.search(query_vec[None, :].astype(np.float32), k)
        return [(int(i), float(s)) for i, s in zip(ids[0], scores[0], strict=False) if i != -1]


class Embedder:
    """Wraps a sentence-transformers model and adds an LRU cache for queries."""

    def __init__(self, model_name: str, cache_size: int = 1024) -> None:
        from sentence_transformers import SentenceTransformer

        log.info("loading embedding model %s", model_name)
        self.model = SentenceTransformer(model_name, device="cpu")
        self.tokenizer = self.model.tokenizer
        self._cache: OrderedDict[str, np.ndarray] = OrderedDict()
        self.cache_size = cache_size
        self.cache_hits = 0

    def embed_passages(self, texts: list[str], batch_size: int = 32) -> np.ndarray:
        return self.model.encode(
            [f"passage: {t}" for t in texts],
            batch_size=batch_size,
            normalize_embeddings=True,
            convert_to_numpy=True,
        )

    def embed_query(self, text: str, use_cache: bool = True) -> np.ndarray:
        if use_cache and text in self._cache:
            self._cache.move_to_end(text)
            self.cache_hits += 1
            return self._cache[text]
        vec = self.model.encode(f"query: {text}", normalize_embeddings=True, convert_to_numpy=True)
        if use_cache:
            self._cache[text] = vec
            if len(self._cache) > self.cache_size:
                self._cache.popitem(last=False)
        return vec

    def embed_sentences(self, texts: list[str]) -> np.ndarray:
        """Symmetric embedding (both sides 'query:') for sentence-vs-sentence checks."""
        return self.model.encode(
            [f"query: {t}" for t in texts], normalize_embeddings=True, convert_to_numpy=True
        )
