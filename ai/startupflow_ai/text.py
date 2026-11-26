"""Text normalisation and tokenisation helpers (Vietnamese-aware).

Why NFC matters: Vietnamese characters such as "ế" can be stored either as one
precomposed code point (NFC) or as "e" + combining circumflex + combining acute
(NFD). They look identical but compare unequal, so BM25 term matching and
exact-match checks silently fail unless every string is normalised first.
"""

from __future__ import annotations

import re
import unicodedata

_WS = re.compile(r"\s+")
_CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
# \w is Unicode-aware in Python 3, so it keeps Vietnamese letters with diacritics.
_TOKEN = re.compile(r"\w+", re.UNICODE)


def normalize(text: str) -> str:
    """NFC-normalise, drop control characters and collapse whitespace."""
    text = unicodedata.normalize("NFC", text)
    text = _CONTROL.sub(" ", text)
    return _WS.sub(" ", text).strip()


def fold_diacritics(text: str) -> str:
    """Remove Vietnamese tone/vowel marks: "Tiền Nhanh" -> "Tien Nhanh".

    Many users type Vietnamese without diacritics, so folding both the query
    and the documents lets lexical search still match them.
    """
    text = text.replace("đ", "d").replace("Đ", "D")
    decomposed = unicodedata.normalize("NFD", text)
    stripped = "".join(c for c in decomposed if unicodedata.category(c) != "Mn")
    return unicodedata.normalize("NFC", stripped)


def tokenize(text: str, fold: bool = True) -> list[str]:
    """Lower-cased syllable tokens for BM25.

    Vietnamese words are often multi-syllable ("ví điện tử"); whitespace
    splitting yields syllables, not words. A proper word segmenter
    (e.g. underthesea, pyvi) would do better; we keep syllables plus
    syllable bigrams in `tokenize_with_bigrams` as a cheap approximation.
    """
    text = normalize(text).lower()
    if fold:
        text = fold_diacritics(text)
    return _TOKEN.findall(text)


def tokenize_with_bigrams(text: str, fold: bool = True) -> list[str]:
    toks = tokenize(text, fold=fold)
    return toks + [f"{a}_{b}" for a, b in zip(toks, toks[1:], strict=False)]
