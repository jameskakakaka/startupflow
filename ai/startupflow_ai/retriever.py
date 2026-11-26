"""Index a chunked corpus once, then search it with dense, BM25 or hybrid retrieval."""

from __future__ import annotations

import logging
import time

from startupflow_ai.bm25 import BM25
from startupflow_ai.chunking import Chunk
from startupflow_ai.dense import Embedder, FaissIndex
from startupflow_ai.hybrid import rrf
from startupflow_ai.text import tokenize

log = logging.getLogger(__name__)

MODES = ("dense", "bm25", "hybrid")


class Retriever:
    def __init__(self, chunks: list[Chunk], embedder: Embedder, bm25_tokenizer=tokenize) -> None:
        t0 = time.perf_counter()
        self.chunks = chunks
        self.embedder = embedder
        self.matrix = embedder.embed_passages([c.text for c in chunks])
        self.faiss = FaissIndex(self.matrix)
        self.bm25 = BM25([c.text for c in chunks], tokenizer=bm25_tokenizer)
        log.info("indexed %d chunks in %.1fs", len(chunks), time.perf_counter() - t0)

    def dense(self, query: str, k: int, use_cache: bool = True) -> list[tuple[int, float]]:
        return self.faiss.search(self.embedder.embed_query(query, use_cache=use_cache), k)

    def search(
        self, query: str, k: int, mode: str = "hybrid", pool: int = 20, use_cache: bool = True
    ) -> list[tuple[int, float]]:
        """Return [(chunk_index, score)] best first.

        For hybrid, each retriever contributes its top `pool` candidates
        to RRF, and the fused list is cut to k.
        """
        if mode == "dense":
            return self.dense(query, k, use_cache)
        if mode == "bm25":
            return self.bm25.search(query, k)
        if mode == "hybrid":
            d = [i for i, _ in self.dense(query, pool, use_cache)]
            b = [i for i, _ in self.bm25.search(query, pool)]
            return rrf([d, b])[:k]
        raise ValueError(f"mode must be one of {MODES}")
