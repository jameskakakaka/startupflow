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
from dataclasses import dataclass

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


@dataclass
class Verdict:
    ok: bool
    citations: list[int]
    inferred: bool = False
    note: str = ""


def _word_set(text: str) -> set[str]:
    from startupflow_ai.text import tokenize

    return set(tokenize(text))


def verify_answer(
    question: str,
    answer: str,
    citations: list[int],
    passages: list[tuple[str, str]],
    all_titles: set[str],
) -> Verdict:
    """Post-generation checks, in order. `passages` = [(title, text)] of the retrieved
    chunks, 1-based like the citations. Any failure means: do not show the answer.

    1. Degenerate output: only citation markers / punctuation, or an echo of the question.
    2. Numbers: every number must be in the cited passages. If the model cited the
       wrong passage number but another retrieved passage contains all the numbers,
       re-attribute the citation (flagged as inferred); otherwise reject.
    3. Entity: the (possibly re-attributed) cited passages must be about the company
       the question names.
    """
    content = re.sub(r"\[\d+\]|\W", "", answer)
    if len(content) < 2:
        return Verdict(False, [], note="degenerate answer")
    a_words, q_words = _word_set(answer), _word_set(question)
    if len(a_words) >= 3 and a_words <= q_words and len(a_words) >= 0.6 * len(q_words):
        return Verdict(False, [], note="answer only repeats the question")

    inferred = False
    cited_text = "\n".join(passages[c - 1][1] for c in citations)
    if unsupported_numbers(answer, cited_text):
        support = [i for i, (_, t) in enumerate(passages, start=1) if not unsupported_numbers(answer, t)]
        if not support:
            return Verdict(False, [], note="numbers not found in any retrieved passage")
        citations, inferred = support[:2], True

    if entity_mismatch(question, [passages[c - 1][0] for c in citations], all_titles):
        return Verdict(False, [], note="entity mismatch between question and cited passages")
    return Verdict(True, citations, inferred)
