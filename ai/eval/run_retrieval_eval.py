"""Retrieval evaluation + ablation over the gold set.

Run:  python eval/run_retrieval_eval.py
Out:  results/retrieval.json, results/retrieval.md

A retrieved chunk counts as relevant if it comes from the gold document AND
contains the gold evidence string. That keeps the label independent of the
chunking strategy: if a fixed-size window cuts the evidence in half, the
chunk is (correctly) not relevant.
"""

from __future__ import annotations

import json
from functools import partial
from pathlib import Path

import numpy as np

from startupflow_ai.bm25 import BM25
from startupflow_ai.chunking import Chunk, chunk_corpus, load_documents
from startupflow_ai.config import AI_DIR, Settings
from startupflow_ai.dense import Embedder
from startupflow_ai.hybrid import rrf
from startupflow_ai.metrics import mrr, recall_at_k
from startupflow_ai.retriever import Retriever
from startupflow_ai.text import normalize, tokenize, tokenize_with_bigrams

GOLD = AI_DIR / "data" / "eval" / "gold.jsonl"
OUT = AI_DIR / "results"
DEPTH = 10


def load_gold(path: Path = GOLD) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def is_relevant(chunk: Chunk, q: dict) -> bool:
    return chunk.doc_id == q["doc_id"] and normalize(q["evidence"]).lower() in chunk.text.lower()


def flags_for(ids: list[int], chunks: list[Chunk], q: dict) -> list[bool]:
    return [is_relevant(chunks[i], q) for i in ids[:DEPTH]]


def summarize(rows: list[tuple[dict, list[bool]]]) -> dict:
    flags = [f for _, f in rows]
    return {
        "n": len(flags),
        "recall@1": recall_at_k(flags, 1),
        "recall@3": recall_at_k(flags, 3),
        "recall@5": recall_at_k(flags, 5),
        "mrr@10": mrr(flags),
    }


def main() -> None:
    s = Settings()
    gold = load_gold()
    answerable = [q for q in gold if q["answerable"]]
    embedder = Embedder(s.embed_model)
    docs = load_documents(s.corpus_dir)

    results: dict = {"configs": {}, "per_question": {}, "abstention": {}}
    for chunking in ("fixed", "fixed30", "heading"):
        chunks = chunk_corpus(docs, chunking)
        retr = Retriever(chunks, embedder)
        texts = [c.text for c in chunks]
        bm25_variants = {
            "bm25_raw": BM25(texts, tokenizer=partial(tokenize, fold=False)),
            "bm25_fold": retr.bm25,  # default: diacritics folded
            "bm25_fold_bigram": BM25(texts, tokenizer=tokenize_with_bigrams),
        }

        def rank(q: str, mode: str, retr=retr, bm25_variants=bm25_variants) -> list[int]:
            if mode.startswith("bm25"):
                return [i for i, _ in bm25_variants[mode].search(q, DEPTH)]
            if mode == "dense":
                return [i for i, _ in retr.dense(q, DEPTH)]
            if mode == "hybrid":
                d = [i for i, _ in retr.dense(q, 20)]
                b = [i for i, _ in retr.bm25.search(q, 20)]
                return [i for i, _ in rrf([d, b])[:DEPTH]]
            raise ValueError(mode)

        for mode in ("bm25_raw", "bm25_fold", "bm25_fold_bigram", "dense", "hybrid"):
            name = f"{chunking}+{mode}"
            rows = [(q, flags_for(rank(q["question"], mode), chunks, q)) for q in answerable]
            entry = {"chunks": len(chunks), "overall": summarize(rows), "by_type": {}}
            for typ in sorted({q["type"] for q in answerable}):
                entry["by_type"][typ] = summarize([r for r in rows if r[0]["type"] == typ])
            results["configs"][name] = entry
            results["per_question"][name] = {
                q["id"]: next((i + 1 for i, f in enumerate(fl) if f), None) for q, fl in rows
            }

        # Abstention: does the top-1 dense cosine separate answerable from no-answer?
        top1 = {q["id"]: retr.dense(q["question"], 1)[0][1] for q in gold}
        ans = np.array([top1[q["id"]] for q in gold if q["answerable"]])
        neg = np.array([top1[q["id"]] for q in gold if not q["answerable"]])
        table = []
        for t in np.arange(0.78, 0.90, 0.01):
            table.append(
                {
                    "threshold": round(float(t), 2),
                    "answerable_kept": float((ans >= t).mean()),
                    "no_answer_rejected": float((neg < t).mean()),
                }
            )
        results["abstention"][chunking] = {
            "answerable_top1": [round(float(x), 4) for x in sorted(ans)],
            "no_answer_top1": [round(float(x), 4) for x in sorted(neg)],
            "sweep": table,
        }

    OUT.mkdir(exist_ok=True)
    (OUT / "retrieval.json").write_text(json.dumps(results, indent=2, ensure_ascii=False))
    (OUT / "retrieval.md").write_text(render_md(results))
    print(render_md(results))


def render_md(r: dict) -> str:
    lines = [
        "## Retrieval ablation (32 answerable questions)",
        "",
        "| Config | #chunks | Recall@1 | Recall@3 | Recall@5 | MRR@10 |",
        "|---|---|---|---|---|---|",
    ]
    for name, e in r["configs"].items():
        o = e["overall"]
        lines.append(
            f"| {name} | {e['chunks']} | {o['recall@1']:.3f} | {o['recall@3']:.3f} "
            f"| {o['recall@5']:.3f} | {o['mrr@10']:.3f} |"
        )
    types = sorted(next(iter(r["configs"].values()))["by_type"])
    lines += [
        "",
        "### Recall@3 by question type",
        "",
        "| Config | "
        + " | ".join(f"{t} (n={next(iter(r['configs'].values()))['by_type'][t]['n']})" for t in types)
        + " |",
        "|---|" + "---|" * len(types),
    ]
    for name, e in r["configs"].items():
        lines.append(f"| {name} | " + " | ".join(f"{e['by_type'][t]['recall@3']:.2f}" for t in types) + " |")
    for chunking, a in r["abstention"].items():
        lines += [
            "",
            f"### Abstention threshold sweep on top-1 dense cosine ({chunking} chunks)",
            "",
            "| threshold | answerable kept | no-answer rejected |",
            "|---|---|---|",
        ]
        for row in a["sweep"]:
            lines.append(
                f"| {row['threshold']:.2f} | {row['answerable_kept']:.2f} | {row['no_answer_rejected']:.2f} |"
            )
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()
