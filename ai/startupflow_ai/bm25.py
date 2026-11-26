"""BM25 (Okapi) written out by hand so every term of the formula is visible.

score(q, d) = sum over query terms t of
    IDF(t) * tf(t,d) * (k1 + 1) / (tf(t,d) + k1 * (1 - b + b * |d| / avgdl))

IDF(t) = ln(1 + (N - df(t) + 0.5) / (df(t) + 0.5))

- tf saturates: the 10th repetition of a word adds far less than the 1st (k1).
- b normalises by document length so long chunks are not favoured.
- Rare terms (low df) get a high IDF, so names like "SoKa" dominate the score.
"""

from __future__ import annotations

import math
from collections import Counter
from collections.abc import Callable, Sequence


class BM25:
    def __init__(
        self,
        docs: Sequence[str],
        tokenizer: Callable[[str], list[str]],
        k1: float = 1.5,
        b: float = 0.75,
    ) -> None:
        self.tokenizer = tokenizer
        self.k1, self.b = k1, b
        self.tfs = [Counter(tokenizer(d)) for d in docs]
        self.lens = [sum(tf.values()) for tf in self.tfs]
        self.n = len(docs)
        self.avgdl = sum(self.lens) / max(self.n, 1)
        df: Counter[str] = Counter()
        for tf in self.tfs:
            df.update(tf.keys())
        self.idf = {t: math.log(1 + (self.n - f + 0.5) / (f + 0.5)) for t, f in df.items()}

    def scores(self, query: str) -> list[float]:
        q_terms = self.tokenizer(query)
        out = []
        for tf, dl in zip(self.tfs, self.lens, strict=False):
            s = 0.0
            norm = self.k1 * (1 - self.b + self.b * dl / self.avgdl)
            for t in q_terms:
                f = tf.get(t, 0)
                if f:
                    s += self.idf[t] * f * (self.k1 + 1) / (f + norm)
            out.append(s)
        return out

    def search(self, query: str, k: int) -> list[tuple[int, float]]:
        scored = sorted(enumerate(self.scores(query)), key=lambda x: x[1], reverse=True)
        return [(i, s) for i, s in scored[:k] if s > 0]
