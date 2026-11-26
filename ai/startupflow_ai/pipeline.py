"""End-to-end RAG: normalise -> retrieve -> gate -> generate -> ground-check."""

from __future__ import annotations

import logging
import time
from functools import cached_property

from startupflow_ai.chunking import chunk_corpus, load_documents
from startupflow_ai.config import Settings
from startupflow_ai.dense import Embedder
from startupflow_ai.generate import NOT_FOUND, Generator, build_context, guess_lang
from startupflow_ai.grounding import entity_mismatch, unsupported_numbers
from startupflow_ai.retriever import Retriever
from startupflow_ai.schemas import AskResponse, Source
from startupflow_ai.text import normalize

log = logging.getLogger(__name__)


class RAGPipeline:
    def __init__(self, settings: Settings | None = None, load_llm: bool = True) -> None:
        self.s = settings or Settings()
        self.embedder = Embedder(self.s.embed_model)
        self.chunks = chunk_corpus(load_documents(self.s.corpus_dir), self.s.chunking)
        self.retriever = Retriever(self.chunks, self.embedder)
        self.titles = {c.title for c in self.chunks}
        self._load_llm = load_llm

    @cached_property
    def generator(self) -> Generator:
        return Generator(self.s.llm_model, self.s.max_new_tokens)

    def ask(self, question: str, top_k: int | None = None, use_cache: bool = True) -> AskResponse:
        timings: dict[str, float] = {}
        question = normalize(question)[: self.s.max_query_chars]
        k = top_k or self.s.top_k

        t0 = time.perf_counter()
        hits = self.retriever.search(question, k, mode=self.s.retrieval, use_cache=use_cache)
        # Gate on the dense similarity of the best chunk: RRF scores are rank-based
        # and say nothing about absolute relevance.
        top_dense = self.retriever.dense(question, 1, use_cache=use_cache)[0][1]
        timings["retrieve"] = (time.perf_counter() - t0) * 1000

        chunks = [self.chunks[i] for i, _ in hits]
        sources = [
            Source(n=n, chunk_id=c.chunk_id, title=c.title, section=c.section, score=round(s, 4), text=c.text)
            for n, (c, (_, s)) in enumerate(zip(chunks, hits, strict=False), start=1)
        ]

        if top_dense < self.s.min_score or not self._load_llm:
            log.info("abstain: top dense score %.3f < %.2f", top_dense, self.s.min_score)
            return AskResponse(
                found=False,
                answer=NOT_FOUND[guess_lang(question)],
                citations=[],
                sources=sources,
                grounded=True,
                unsupported_numbers=[],
                timings_ms=timings,
                note=f"retrieval gate: top score {top_dense:.3f} < {self.s.min_score}",
            )

        t1 = time.perf_counter()
        llm, _raw = self.generator.answer(question, chunks)
        timings["generate"] = (time.perf_counter() - t1) * 1000

        def abstain(note: str) -> AskResponse:
            return AskResponse(
                found=False,
                answer=NOT_FOUND[guess_lang(question)],
                citations=[],
                sources=sources,
                grounded=True,
                unsupported_numbers=[],
                timings_ms=timings,
                note=note,
            )

        if not llm.found:
            return abstain("model: not in context")
        cited_chunks = [chunks[c - 1] for c in llm.citations]
        if entity_mismatch(question, [c.title for c in cited_chunks], self.titles):
            log.info("abstain: cited passages are about a different company")
            return abstain("entity mismatch between question and cited passages")
        bad_numbers = unsupported_numbers(llm.answer, build_context(cited_chunks))
        return AskResponse(
            found=True,
            answer=llm.answer,
            citations=llm.citations,
            sources=sources,
            grounded=not bad_numbers,
            unsupported_numbers=bad_numbers,
            citations_inferred=llm.citations_inferred,
            timings_ms=timings,
        )
