"""Reciprocal Rank Fusion (RRF) for combining BM25 and dense rankings.

BM25 scores (unbounded) and cosine scores (-1..1) are on different scales, so
adding them directly is meaningless. RRF ignores raw scores and only uses
ranks:  rrf(d) = sum over rankers r of 1 / (k + rank_r(d)),  with k = 60.
A document ranked high by either retriever rises; one ranked high by both
rises most.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence


def rrf(rankings: Sequence[Sequence[int]], k: int = 60) -> list[tuple[int, float]]:
    scores: dict[int, float] = defaultdict(float)
    for ranking in rankings:
        for rank, doc in enumerate(ranking, start=1):
            scores[doc] += 1.0 / (k + rank)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)
