"""Retrieval metrics.

Recall@k  = fraction of questions where at least one relevant chunk is in the top k.
            (With one gold fact per question this is also called hit rate@k.)
MRR       = mean over questions of 1 / rank of the first relevant chunk
            (0 if none is retrieved). It rewards putting the evidence first.
"""

from __future__ import annotations

from collections.abc import Sequence


def recall_at_k(relevant_flags: Sequence[Sequence[bool]], k: int) -> float:
    if not relevant_flags:
        return 0.0
    return sum(any(flags[:k]) for flags in relevant_flags) / len(relevant_flags)


def mrr(relevant_flags: Sequence[Sequence[bool]]) -> float:
    if not relevant_flags:
        return 0.0
    total = 0.0
    for flags in relevant_flags:
        for rank, rel in enumerate(flags, start=1):
            if rel:
                total += 1.0 / rank
                break
    return total / len(relevant_flags)
