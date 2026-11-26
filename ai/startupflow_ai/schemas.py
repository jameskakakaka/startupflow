"""Pydantic schemas: the contract for LLM output and for the HTTP API."""

from __future__ import annotations

import json
import re

from pydantic import BaseModel, Field, ValidationError, field_validator

from startupflow_ai.text import normalize


class LLMAnswer(BaseModel):
    """What the LLM must return. Anything else is rejected, not guessed at."""

    found: bool
    answer: str = Field(max_length=1200)
    citations: list[int] = Field(default_factory=list)


_JSON_OBJ = re.compile(r"\{.*\}", re.S)


def parse_llm_answer(raw: str, n_context: int) -> LLMAnswer | None:
    """Extract and validate the JSON object; drop citations outside [1, n_context].

    Returns None if the output is not valid JSON that matches the schema, so
    the caller can retry or fall back instead of crashing or trusting garbage.
    """
    match = _JSON_OBJ.search(raw)
    if not match:
        return None
    try:
        parsed = LLMAnswer.model_validate(json.loads(match.group(0)))
    except (json.JSONDecodeError, ValidationError):
        return None
    parsed.citations = sorted({c for c in parsed.citations if 1 <= c <= n_context})
    if parsed.found and not parsed.citations:
        # An answer with no valid citation is treated as ungrounded.
        return LLMAnswer(found=False, answer=parsed.answer, citations=[])
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
    timings_ms: dict[str, float]
