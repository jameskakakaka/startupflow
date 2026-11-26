"""Configuration read from environment variables (see ai/.env.example)."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

AI_DIR = Path(__file__).resolve().parents[1]


def _env(name: str, default: str) -> str:
    return os.environ.get(name, default)


@dataclass(frozen=True)
class Settings:
    corpus_dir: Path = field(
        default_factory=lambda: Path(_env("SF_CORPUS_DIR", str(AI_DIR / "data" / "corpus")))
    )
    embed_model: str = field(default_factory=lambda: _env("SF_EMBED_MODEL", "intfloat/multilingual-e5-small"))
    llm_model: str = field(default_factory=lambda: _env("SF_LLM_MODEL", "Qwen/Qwen2.5-0.5B-Instruct"))
    chunking: str = field(default_factory=lambda: _env("SF_CHUNKING", "fixed"))
    retrieval: str = field(default_factory=lambda: _env("SF_RETRIEVAL", "hybrid"))
    top_k: int = field(default_factory=lambda: int(_env("SF_TOP_K", "4")))
    # Below this top-1 dense cosine we answer "not found" without calling the LLM.
    min_score: float = field(default_factory=lambda: float(_env("SF_MIN_SCORE", "0.80")))
    max_new_tokens: int = field(default_factory=lambda: int(_env("SF_MAX_NEW_TOKENS", "160")))
    request_timeout_s: float = field(default_factory=lambda: float(_env("SF_TIMEOUT_S", "60")))
    max_query_chars: int = 500
