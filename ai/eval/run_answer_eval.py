"""End-to-end answer evaluation of the default pipeline (fixed chunks + hybrid, top-4, Qwen2.5-0.5B).

Run:  python eval/run_answer_eval.py
Out:  results/answers.jsonl (one row per question, for manual review)
      results/answers.md    (summary tables)

Metrics
- answer accuracy (answerable): found=True AND the answer contains a gold keyword
  (accent/case-insensitive). It is a strict, cheap proxy; manual review checks it.
- correct abstention (no-answer): found=False.
- citation precision: share of cited passages that contain the gold evidence.
- numeric hallucination flag: the answer has a number not present in the cited passages.
- LLM-as-judge (experiment): the same 0.5B model is asked whether the answer is
  supported by the passages; we report its agreement with the keyword+evidence label.
"""

from __future__ import annotations

import json
import statistics
import time

import numpy as np

from startupflow_ai.config import AI_DIR, Settings
from startupflow_ai.grounding import min_sentence_support
from startupflow_ai.pipeline import RAGPipeline
from startupflow_ai.text import fold_diacritics

GOLD = AI_DIR / "data" / "eval" / "gold.jsonl"
OUT = AI_DIR / "results"

JUDGE_PROMPT = """You check answers for hallucinations.
<context>
{context}
</context>
Question: {question}
Answer: {answer}
Is every fact in the Answer stated in the context? Reply with exactly one word: yes or no."""


def _f(s: str) -> str:
    return fold_diacritics(s.lower())


def keyword_correct(answer: str, q: dict) -> bool:
    a = _f(answer)
    if q["answer_all"]:
        return all(_f(k) in a for k in q["answer_all"])
    return any(_f(k) in a for k in q["answer_any"])


def judge(pipe: RAGPipeline, question: str, answer: str, context: str) -> bool | None:
    gen = pipe.generator
    msg = [
        {"role": "user", "content": JUDGE_PROMPT.format(context=context, question=question, answer=answer)}
    ]
    old = gen.max_new_tokens
    gen.max_new_tokens = 3
    try:
        out = gen._complete(msg).strip().lower()
    finally:
        gen.max_new_tokens = old
    if out.startswith("yes"):
        return True
    if out.startswith("no"):
        return False
    return None


def pct(xs: list[bool]) -> str:
    return f"{sum(xs)}/{len(xs)} = {sum(xs) / len(xs):.2f}" if xs else "n/a"


def main() -> None:
    s = Settings()
    gold = [json.loads(line) for line in GOLD.read_text(encoding="utf-8").splitlines() if line.strip()]
    pipe = RAGPipeline(s)
    _ = pipe.generator  # load the LLM before timing

    rows = []
    for q in gold:
        t0 = time.perf_counter()
        resp = pipe.ask(q["question"], use_cache=False)
        total_ms = (time.perf_counter() - t0) * 1000
        cited = [resp.sources[c - 1] for c in resp.citations]
        evid = (q["evidence"] or "").lower()
        row = {
            "id": q["id"],
            "type": q["type"],
            "lang": q["lang"],
            "question": q["question"],
            "answerable": q["answerable"],
            "found": resp.found,
            "answer": resp.answer,
            "citations": [c.chunk_id for c in cited],
            "retrieved": [x.chunk_id for x in resp.sources],
            "evidence_retrieved": bool(evid) and any(evid in x.text.lower() for x in resp.sources),
            "keyword_correct": resp.found and q["answerable"] and keyword_correct(resp.answer, q),
            "citation_precision": (
                sum(evid in c.text.lower() for c in cited) / len(cited) if (cited and evid) else None
            ),
            "unsupported_numbers": resp.unsupported_numbers,
            "citations_inferred": resp.citations_inferred,
            "note": resp.note,
            "latency_ms": round(total_ms, 1),
        }
        if resp.found:
            ctx = "\n".join(c.text for c in cited)
            row["min_sentence_support"] = round(
                min_sentence_support(resp.answer, ctx, pipe.embedder.embed_sentences), 3
            )
            row["judge_supported"] = judge(pipe, q["question"], resp.answer, ctx)
        rows.append(row)
        print(
            f"{q['id']} found={resp.found} ok={row['keyword_correct']} {total_ms:6.0f}ms {resp.answer[:80]!r}"
        )

    OUT.mkdir(exist_ok=True)
    with (OUT / "answers.jsonl").open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    md = render(rows)
    (OUT / "answers.md").write_text(md)
    print(md)


def render(rows: list[dict]) -> str:
    ans = [r for r in rows if r["answerable"]]
    neg = [r for r in rows if not r["answerable"]]
    found = [r for r in rows if r["found"]]
    cps = [r["citation_precision"] for r in found if r["citation_precision"] is not None]
    lat = [r["latency_ms"] for r in rows if r["found"]]
    lat_abstain = [r["latency_ms"] for r in rows if not r["found"]]
    # Judge agreement vs our reference label "correct" (keyword match on an answerable q).
    judged = [r for r in found if r.get("judge_supported") is not None]
    agree = [r["judge_supported"] == bool(r["keyword_correct"]) for r in judged]
    flagged = [r for r in found if r["unsupported_numbers"]]
    lines = [
        f"## End-to-end answer evaluation (fixed+hybrid, top-4, {Settings().llm_model}, CPU)",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| Answer accuracy, answerable (keyword match) | {pct([bool(r['keyword_correct']) for r in ans])} |",
        f"| Evidence in top-4 context, answerable | {pct([r['evidence_retrieved'] for r in ans])} |",
        f"| False abstention, answerable | {pct([not r['found'] for r in ans])} |",
        f"| Correct abstention, no-answer | {pct([not r['found'] for r in neg])} |",
        f"| Citation precision (mean over answered) | {np.mean(cps):.2f} (n={len(cps)}) |"
        if cps
        else "| Citation precision | n/a |",
        f"| Citations inferred post-hoc | {sum(r['citations_inferred'] for r in found)}/{len(found)} |",
        f"| Abstained by entity check | {sum('entity' in r['note'] for r in rows)} |",
        f"| Answers flagged by numeric check | {len(flagged)}/{len(found)} |",
        f"| ...of which wrong by keyword | {sum(not r['keyword_correct'] for r in flagged)}/{len(flagged)} |",
        f"| LLM-judge (0.5B) agreement with keyword label | {pct(agree)} |",
        f"| LLM-judge said 'supported' | {sum(r['judge_supported'] for r in judged)}/{len(judged)} |",
        f"| Latency when answering, p50 / max (ms) | {statistics.median(lat):.0f} / {max(lat):.0f} |"
        if lat
        else "",
        f"| Latency when abstaining, p50 (ms) | {statistics.median(lat_abstain):.0f} |"
        if lat_abstain
        else "",
        "",
        "### By question type (answer accuracy or correct abstention)",
        "",
        "| Type | n | Score |",
        "|---|---|---|",
    ]
    for typ in sorted({r["type"] for r in rows}):
        sub = [r for r in rows if r["type"] == typ]
        ok = [(not r["found"]) if typ == "no_answer" else bool(r["keyword_correct"]) for r in sub]
        lines.append(f"| {typ} | {len(sub)} | {sum(ok) / len(ok):.2f} |")
    return "\n".join(x for x in lines if x is not None) + "\n"


if __name__ == "__main__":
    main()
