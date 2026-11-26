"""Pydantic schemas: the contract for LLM output and for the HTTP API."""

from __future__ import annotations

import json
import re

from pydantic import BaseModel, Field, ValidationError, field_validator

from startupflow_ai.text import fold_diacritics, normalize


class LLMAnswer(BaseModel):
    """What the LLM must return. `found` and `answer` are strictly validated."""

    found: bool
    answer: str = Field(default="", max_length=1200)
    citations: list[int] = Field(default_factory=list)
    citations_inferred: bool = False


_JSON_OBJ = re.compile(r"\{.*\}", re.S)
_CIT_ARRAY = re.compile(r'"citations"\s*:\s*\[(.*?)\]', re.S)
_BRACKET_NUM = re.compile(r"^\s*\[?\s*(\d+)\s*\]?\s*$")
_NUM = re.compile(r"\d+(?:[.,]\d+)*")


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"\w+", fold_diacritics(text.lower())))


def _match_passage(text: str, passages: list[str]) -> int | None:
    """Map a quoted snippet back to the passage it came from (1-based), by token overlap."""
    toks = _tokens(text)
    if not toks or not passages:
        return None
    overlaps = [len(toks & _tokens(p)) / len(toks) for p in passages]
    best = max(range(len(passages)), key=overlaps.__getitem__)
    return best + 1 if overlaps[best] >= 0.6 else None


def _coerce_citation(item: object, passages: list[str]) -> int | None:
    """Small models write citations as 2, "2", "[2]", {"passage_number": 2} or a quote."""
    if isinstance(item, bool):
        return None
    if isinstance(item, int):
        return item
    if isinstance(item, str):
        m = _BRACKET_NUM.match(item)
        return int(m.group(1)) if m else _match_passage(item, passages)
    if isinstance(item, dict):
        for key, val in item.items():
            if any(k in key.lower() for k in ("passage", "number", "id", "index")):
                c = _coerce_citation(val, passages)
                if c is not None:
                    return c
        if isinstance(item.get("text"), str):
            return _match_passage(item["text"], passages)
    return None


def _infer_citations(answer: str, passages: list[str]) -> list[int]:
    """Post-hoc attribution: passages that contain every number in the answer,
    or (if the answer has no numbers) the passage with the highest token overlap."""
    nums = {n.replace(",", ".") for n in _NUM.findall(answer)}
    if nums:
        hits = [
            i
            for i, p in enumerate(passages, start=1)
            if nums <= {n.replace(",", ".") for n in _NUM.findall(p)}
        ]
        return hits[:2]
    best = _match_passage(answer, passages)
    return [best] if best else []


def _load_json(raw: str) -> dict | None:
    match = _JSON_OBJ.search(raw)
    if not match:
        return None
    text = match.group(0)
    for candidate in (
        text,
        _CIT_ARRAY.sub(lambda m: '"citations": [' + ",".join(re.findall(r"\d+", m.group(1))) + "]", text),
    ):
        try:
            data = json.loads(candidate)
            return data if isinstance(data, dict) else None
        except json.JSONDecodeError:
            continue
    return None


def parse_llm_answer(raw: str, n_context: int, passages: list[str] | None = None) -> LLMAnswer | None:
    """Parse, repair and validate the LLM output.

    - `found`/`answer` must validate against the schema, otherwise None (caller retries).
    - Citations are coerced from common malformed shapes, then range-checked.
    - If found=true but no citation survives, citations are inferred from the passages
      (flagged with citations_inferred). If that also fails, the answer is downgraded
      to not-found: we never return an answer that cannot be tied to a source.
    """
    passages = passages or []
    data = _load_json(raw)
    if data is None:
        return None
    raw_cits = data.pop("citations", [])
    if not isinstance(raw_cits, list):
        raw_cits = [raw_cits]
    try:
        parsed = LLMAnswer.model_validate({**data, "citations": []})
    except ValidationError:
        return None
    cits = {_coerce_citation(c, passages) for c in raw_cits}
    parsed.citations = sorted(c for c in cits if c is not None and 1 <= c <= n_context)
    if parsed.found and not parsed.answer.strip():
        return LLMAnswer(found=False)
    if parsed.found and not parsed.citations:
        inferred = _infer_citations(parsed.answer, passages)
        if not inferred:
            return LLMAnswer(found=False, answer=parsed.answer)
        parsed.citations, parsed.citations_inferred = inferred, True
    return parsed


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=500)
    top_k: int = Field(default=4, ge=1, le=10)

    @field_validator("question")
    @classmethod
    def _clean(cls, v: str) -> str:
        v = normalize(v)
        if len(v) < 3:
            raise ValueError("question is empty after normalisation")
        return v


class Source(BaseModel):
    n: int
    chunk_id: str
    title: str
    section: str
    score: float
    text: str


class AskResponse(BaseModel):
    found: bool
    answer: str
    citations: list[int]
    sources: list[Source]
    grounded: bool
    unsupported_numbers: list[str]
    citations_inferred: bool = False
    note: str = ""
    timings_ms: dict[str, float]
