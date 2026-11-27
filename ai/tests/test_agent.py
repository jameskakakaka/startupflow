"""Agent-loop tests with a scripted fake LLM: no model needed, fully deterministic."""

import json

import pytest

from startupflow_ai.agent import build_startup_table, make_tools, parse_tool_calls, run_agent, safe_calc
from startupflow_ai.chunking import Chunk


def chunk(doc, title, text):
    return Chunk(f"{doc}#f0", doc, title, "", f"{title} | {text}")


CHUNKS = [
    chunk(
        "paynest",
        "PayNest",
        "QR payments. Stage: Seed. Pipeline status: Due Diligence. Raising 2.5 million USD.",
    ),
    chunk("vixanh", "VíXanh", "Ví điện tử. Giai đoạn: Series A. Trạng thái pipeline: Reviewing."),
    chunk(
        "carelink",
        "CareLink",
        "Telemedicine. Stage: Seed. Pipeline status: Due Diligence. Raising 2 million USD.",
    ),
]
TOOLS = make_tools(
    lambda q: [c for c in CHUNKS if q.lower().split()[0] in c.text.lower()], build_startup_table(CHUNKS)
)


def scripted(*replies):
    it = iter(replies)
    seen = []

    def chat(messages, tools):
        seen.append(messages)
        return next(it)

    chat.seen = seen
    return chat


def call(name, **args):
    return f"<tool_call>\n{json.dumps({'name': name, 'arguments': args})}\n</tool_call>"


def test_table_parses_vi_and_en_memos():
    assert build_startup_table(CHUNKS) == [
        {"name": "PayNest", "stage": "Seed", "status": "Due Diligence"},
        {"name": "VíXanh", "stage": "Series A", "status": "Reviewing"},
        {"name": "CareLink", "stage": "Seed", "status": "Due Diligence"},
    ]


def test_multi_step_search_then_calculate():
    chat = scripted(
        call("search_memos", query="PayNest raising"), call("calculator", expression="2.5 + 2"), "4.5M USD"
    )
    res = run_agent("PayNest + CareLink raising?", chat, TOOLS)
    assert [s.tool for s in res.steps] == ["search_memos", "calculator"]
    assert res.steps[1].result == "4.5"
    assert res.answer == "4.5M USD"
    assert chat.seen[-1][-1]["role"] == "tool"  # the tool result was fed back to the model


def test_list_filter_is_accent_and_case_insensitive():
    res = run_agent("?", scripted(call("list_startups", status="due diligence"), "ok"), TOOLS)
    assert "PayNest" in res.steps[0].result and "VíXanh" not in res.steps[0].result


def test_bad_tool_and_bad_args_are_reported_not_raised():
    chat = scripted(
        call("delete_db"),
        call("calculator", expr="1+1"),
        call("calculator", expression="__import__('os')"),
        "x",
    )
    res = run_agent("?", chat, TOOLS)
    assert [s.ok for s in res.steps] == [False, False, False]
    assert "unknown tool" in res.steps[0].result
    assert "invalid arguments" in res.steps[1].result
    assert res.steps[2].result.startswith("Error")


def test_step_limit():
    res = run_agent("?", scripted(*[call("calculator", expression="1")] * 5), TOOLS, max_steps=3)
    assert res.stopped == "max_steps" and len(res.steps) == 3


def test_parse_tool_calls_handles_string_arguments():
    raw = '<tool_call>{"name": "calculator", "arguments": "{\\"expression\\": \\"1+1\\"}"}</tool_call>'
    assert parse_tool_calls(raw) == [{"name": "calculator", "arguments": {"expression": "1+1"}}]


@pytest.mark.parametrize(
    "expr,val", [("2.5 + 2", 4.5), ("15% * 96", 14.4), ("(1,1) * 2", 2.2), ("-3 ** 2", -9)]
)
def test_safe_calc(expr, val):
    assert safe_calc(expr) == pytest.approx(val)


@pytest.mark.parametrize("expr", ["__import__('os').system('ls')", "a + 1", "2 ** 1000", "[1, 2]"])
def test_safe_calc_rejects(expr):
    with pytest.raises((ValueError, SyntaxError)):
        safe_calc(expr)
