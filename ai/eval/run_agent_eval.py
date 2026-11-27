"""Evaluate the tool-calling agent on 8 hand-written tasks with the real local LLM.

Run:  python eval/run_agent_eval.py
Out:  results/agent.jsonl (full step logs), results/agent.md

Per task we check:
- tool selection: every expected tool was called at least once (and none for out-of-scope)
- answer: all expected keywords appear in the final answer (accent/case-insensitive)
"""

from __future__ import annotations

import json
import time

from startupflow_ai.agent import build_startup_table, make_tools, qwen_chat, run_agent
from startupflow_ai.config import AI_DIR, Settings
from startupflow_ai.pipeline import RAGPipeline
from startupflow_ai.text import fold_diacritics

OUT = AI_DIR / "results"

TASKS = [
    (
        "a1",
        "Which startups are in Due Diligence?",
        ["list_startups"],
        ["PayNest", "SoKa Lend", "MekongFresh", "CareLink", "LươngSớm"],
    ),
    ("a2", "Startup nào đang ở trạng thái Passed?", ["list_startups"], ["CreditBee", "ThuốcRẻ"]),
    (
        "a3",
        "List the Seed-stage startups that are in Reviewing.",
        ["list_startups"],
        ["AgriLoop", "ShipNhanh", "Insurely"],
    ),
    ("a4", "VíXanh đang gọi vốn bao nhiêu?", ["search_memos"], ["6 triệu"]),
    ("a5", "What is 15% of 96 billion VND? Answer in billion VND.", ["calculator"], ["14.4"]),
    (
        "a6",
        "How much are PayNest and CareLink raising in total, in million USD?",
        ["search_memos", "calculator"],
        ["4.5"],
    ),
    ("a7", "What is SoKa Lend's NPL ratio multiplied by 2?", ["search_memos", "calculator"], ["2.2"]),
    ("a8", "What's the weather in Hanoi today?", [], []),
]


def f(s: str) -> str:
    return fold_diacritics(s.lower())


def main() -> None:
    pipe = RAGPipeline(Settings())
    table = build_startup_table(pipe.chunks)

    def search(q: str):
        return [pipe.chunks[i] for i, _ in pipe.retriever.search(q, 3, mode="hybrid")]

    tools = make_tools(search, table)
    chat = qwen_chat(pipe.generator)
    rows = []
    for tid, q, exp_tools, exp_kw in TASKS:
        t0 = time.perf_counter()
        res = run_agent(q, chat, tools)
        used = [s.tool for s in res.steps]
        tool_ok = (not used) if not exp_tools else all(t in used for t in exp_tools)
        ans_ok = all(f(k) in f(res.answer) for k in exp_kw) if exp_kw else (not used)
        row = {
            "id": tid,
            "question": q,
            "expected_tools": exp_tools,
            "used_tools": used,
            "tool_ok": tool_ok,
            "answer_ok": ans_ok,
            "answer": res.answer,
            "stopped": res.stopped,
            "steps": [s.__dict__ for s in res.steps],
            "seconds": round(time.perf_counter() - t0, 1),
        }
        rows.append(row)
        print(
            f"{tid} tools={used} tool_ok={tool_ok} answer_ok={ans_ok} {row['seconds']}s | {res.answer[:90]!r}"
        )

    OUT.mkdir(exist_ok=True)
    with (OUT / "agent.jsonl").open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    n = len(rows)
    lines = [
        f"## Tool-calling agent ({Settings().llm_model}, CPU, max 4 steps), {n} tasks",
        "",
        f"- Tool selection correct: {sum(r['tool_ok'] for r in rows)}/{n}",
        f"- Final answer correct: {sum(r['answer_ok'] for r in rows)}/{n}",
        f"- Invalid tool calls (unknown tool / bad args): "
        f"{sum(not s['ok'] for r in rows for s in r['steps'])} of {sum(len(r['steps']) for r in rows)} calls",
        "",
        "| id | question | expected tools | used tools | tool ok | answer ok | s |",
        "|---|---|---|---|---|---|---|",
    ]
    lines += [
        f"| {r['id']} | {r['question']} | {', '.join(r['expected_tools']) or '(none)'} | "
        f"{', '.join(r['used_tools']) or '(none)'} | {'✅' if r['tool_ok'] else '❌'} | "
        f"{'✅' if r['answer_ok'] else '❌'} | {r['seconds']} |"
        for r in rows
    ]
    (OUT / "agent.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
