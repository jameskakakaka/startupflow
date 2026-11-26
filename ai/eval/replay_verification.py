"""Replay the post-generation verification layer on saved answers (no LLM calls).

Generation is greedy, so it is deterministic: changing only the checks that run
*after* the LLM can be evaluated exactly by re-applying them to saved outputs.

Run:  python eval/replay_verification.py results/answers_v2.jsonl
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from startupflow_ai.chunking import chunk_corpus, load_documents
from startupflow_ai.config import Settings
from startupflow_ai.grounding import verify_answer


def main(path: str) -> None:
    s = Settings()
    chunks = {c.chunk_id: c for c in chunk_corpus(load_documents(s.corpus_dir), s.chunking)}
    titles = {c.title for c in chunks.values()}
    rows = [json.loads(x) for x in Path(path).read_text(encoding="utf-8").splitlines()]
    out = []
    for r in rows:
        r = dict(r)
        if r["found"]:
            passages = [(chunks[i].title, chunks[i].text) for i in r["retrieved"]]
            cits = [r["retrieved"].index(c) + 1 for c in r["citations"]]
            v = verify_answer(r["question"], r["answer"], cits, passages, titles)
            r["verify_note"] = v.note
            if not v.ok:
                r["found"], r["keyword_correct"] = False, False
        out.append(r)

    ans = [r for r in out if r["answerable"]]
    neg = [r for r in out if not r["answerable"]]
    answered = [r for r in out if r["found"]]
    correct = sum(bool(r["keyword_correct"]) for r in ans)
    print(f"answer accuracy (answerable): {correct}/{len(ans)} = {correct / len(ans):.2f}")
    print(f"false abstention:             {sum(not r['found'] for r in ans)}/{len(ans)}")
    print(f"correct abstention (no-ans):  {sum(not r['found'] for r in neg)}/{len(neg)}")
    print(f"answer precision (answered):  {correct}/{len(answered)} = {correct / max(len(answered), 1):.2f}")
    for r in out:
        if r.get("verify_note"):
            kind = "answerable" if r["answerable"] else "no-answer"
            print(f"  rejected {r['id']} ({kind}): {r['verify_note']}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "results/answers_v2.jsonl")
