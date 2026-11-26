"""Cheap hallucination checks that do not need a second LLM.

1. Numeric check: every number in the answer must appear in the cited
   chunks. In finance memos most damaging hallucinations are wrong numbers
   (valuation, NPL ratio, ...), and this check catches them deterministically.
2. Semantic check: each answer sentence must be close (cosine) to at least one
   sentence of the cited chunks. It is weaker, because a paraphrase with a
   wrong entity can still score high, so it is reported, not trusted alone.
"""

from __future__ import annotations

import re
from collections.abc import Callable

import numpy as np

_NUM = re.compile(r"\d+(?:[.,]\d+)*")
_SENT = re.compile(r"(?<=[.!?])\s+")


def _number_forms(text: str) -> set[str]:
    forms = set()
    for m in _NUM.findall(text):
        forms.add(m.replace(",", "."))  # "2,5" (vi) == "2.5" (en)
        forms.add(re.sub(r"[.,]", "", m))  # "1.350" == "1,350" == "1350"
    return forms


def unsupported_numbers(answer: str, context: str) -> list[str]:
    ctx = _number_forms(context)
    bad = []
    for m in _NUM.findall(answer):
        if m.replace(",", ".") not in ctx and re.sub(r"[.,]", "", m) not in ctx:
            bad.append(m)
    return bad


def split_sentences(text: str) -> list[str]:
    return [s.strip() for s in _SENT.split(text) if s.strip()]


def min_sentence_support(answer: str, context: str, embed: Callable[[list[str]], np.ndarray]) -> float:
    """Lowest, over answer sentences, of the best cosine to any context sentence."""
    a_sents, c_sents = split_sentences(answer), split_sentences(context)
    if not a_sents or not c_sents:
        return 0.0
    a, c = embed(a_sents), embed(c_sents)
    return float((a @ c.T).max(axis=1).min())


def _compact(text: str) -> str:
    """'NôngTrại360' / 'nong trai 360' -> 'nongtrai360' for robust name matching."""
    from startupflow_ai.text import fold_diacritics

    return re.sub(r"[^a-z0-9]", "", fold_diacritics(text.lower()))


def entities_in_question(question: str, titles: set[str]) -> set[str]:
    """Company names (document titles) mentioned in the question, accent/space-insensitive."""
    q = _compact(question)
    return {t for t in titles if _compact(t) and _compact(t) in q}


def entity_mismatch(question: str, cited_titles: list[str], all_titles: set[str]) -> bool:
    """True if the question names a company but none of the cited passages is about it.

    Catches cross-entity hallucination: asked about ShipNhanh, answered with a
    number from HọcVui's memo. The numeric check cannot see this, because the
    number really is in the (wrong) cited passage.
    """
    asked = entities_in_question(question, all_titles)
    return bool(asked) and not (asked & set(cited_titles))
