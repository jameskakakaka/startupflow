"""A small tool-calling agent, written without an agent framework.

Loop (max `max_steps`):
  1. Send the conversation plus tool schemas to the LLM (Qwen2.5 chat template, `tools=`).
  2. If the reply contains <tool_call>{"name": ..., "arguments": {...}}</tool_call>:
     validate the arguments with that tool's Pydantic model, run the tool, append
     the result as a `tool` message, and log the step. Go to 1.
  3. Otherwise the reply is the final answer.

Safety: unknown tools and invalid arguments are returned to the model as error messages
(they never crash the loop); the calculator parses with `ast` and allows only arithmetic;
tool output is truncated before it goes back into the prompt.
"""

from __future__ import annotations

import ast
import json
import logging
import operator
import re
import time
from collections.abc import Callable
from dataclasses import dataclass, field

from pydantic import BaseModel, Field, ValidationError

from startupflow_ai.chunking import Chunk
from startupflow_ai.text import fold_diacritics

log = logging.getLogger(__name__)

SYSTEM = (
    "You are an assistant for a venture-capital team. Use the tools to look up facts about the "
    "startups in the deal pipeline; never invent numbers. Use `calculator` for any arithmetic. "
    "If the question is not about the startups, answer that you can only help with the deal "
    "pipeline, without calling tools. Answer briefly, in the language of the question."
)

# ---------------------------------------------------------------- tools


class SearchArgs(BaseModel):
    query: str = Field(min_length=2, max_length=300, description="What to look up in the deal memos")


class CalcArgs(BaseModel):
    expression: str = Field(max_length=100, description="Arithmetic expression, e.g. '2.5 + 2'")


class ListArgs(BaseModel):
    status: str | None = Field(default=None, description="New | Reviewing | Due Diligence | Passed")
    stage: str | None = Field(default=None, description="Pre-Seed | Seed | Series A")


_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def safe_calc(expression: str) -> float:
    """Evaluate +, -, *, /, ** and parentheses on numbers. Anything else raises ValueError."""

    def ev(node: ast.AST) -> float:
        if isinstance(node, ast.Constant) and isinstance(node.value, int | float):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
            if isinstance(node.op, ast.Pow) and abs(ev(node.right)) > 10:
                raise ValueError("exponent too large")
            return _OPS[type(node.op)](ev(node.left), ev(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
            return _OPS[type(node.op)](ev(node.operand))
        raise ValueError(f"unsupported expression: {ast.dump(node)[:40]}")

    expr = expression.replace(",", ".").replace("%", "/100")
    return ev(ast.parse(expr, mode="eval").body)


_STAGE_STATUS = re.compile(
    r"(?:Stage|Giai đoạn): (?P<stage>[^.]+)\. (?:Pipeline status|Trạng thái pipeline): (?P<status>[^.]+)\."
)


def build_startup_table(chunks: list[Chunk]) -> list[dict[str, str]]:
    """Structured view (name, stage, status) parsed from each memo's first chunk."""
    rows, seen = [], set()
    for c in chunks:
        m = _STAGE_STATUS.search(c.text)
        if m and c.doc_id not in seen:
            seen.add(c.doc_id)
            rows.append({"name": c.title, "stage": m["stage"].strip(), "status": m["status"].strip()})
    return rows


def _same(a: str, b: str) -> bool:
    return fold_diacritics(a.lower()).strip() == fold_diacritics(b.lower()).strip()


@dataclass
class Tool:
    name: str
    description: str
    args_model: type[BaseModel]
    fn: Callable[[BaseModel], str]

    def schema(self) -> dict:
        params = self.args_model.model_json_schema()
        params.pop("title", None)
        return {
            "type": "function",
            "function": {"name": self.name, "description": self.description, "parameters": params},
        }


def make_tools(search: Callable[[str], list[Chunk]], table: list[dict[str, str]]) -> dict[str, Tool]:
    def do_search(a: SearchArgs) -> str:
        return "\n".join(f"[{c.chunk_id}] {c.text}" for c in search(a.query))

    def do_calc(a: CalcArgs) -> str:
        return f"{safe_calc(a.expression):g}"

    def do_list(a: ListArgs) -> str:
        rows = [
            r
            for r in table
            if (a.status is None or _same(r["status"], a.status))
            and (a.stage is None or _same(r["stage"], a.stage))
        ]
        return json.dumps(rows, ensure_ascii=False) if rows else "[] (no startup matches)"

    tools = [
        Tool(
            "search_memos", "Search the deal memos (Vietnamese or English) for facts.", SearchArgs, do_search
        ),
        Tool("calculator", "Exact arithmetic on numbers.", CalcArgs, do_calc),
        Tool(
            "list_startups",
            "List startups in the pipeline, filtered by status and/or stage.",
            ListArgs,
            do_list,
        ),
    ]
    return {t.name: t for t in tools}


# ---------------------------------------------------------------- loop

_TOOL_CALL = re.compile(r"<tool_call>\s*(\{.*?\})\s*</tool_call>", re.S)


@dataclass
class Step:
    step: int
    tool: str
    arguments: dict
    result: str
    ok: bool
    ms: float


@dataclass
class AgentResult:
    answer: str
    steps: list[Step] = field(default_factory=list)
    stopped: str = "final_answer"  # or "max_steps"


def parse_tool_calls(text: str) -> list[dict]:
    calls = []
    for m in _TOOL_CALL.finditer(text):
        try:
            obj = json.loads(m.group(1))
        except json.JSONDecodeError:
            calls.append({"name": "__invalid__", "arguments": {}, "raw": m.group(1)[:200]})
            continue
        args = obj.get("arguments", {})
        if isinstance(args, str):  # some models emit arguments as a JSON string
            try:
                args = json.loads(args)
            except json.JSONDecodeError:
                args = {}
        calls.append({"name": obj.get("name", ""), "arguments": args if isinstance(args, dict) else {}})
    return calls


ChatFn = Callable[[list[dict], list[dict]], str]


def run_agent(question: str, chat: ChatFn, tools: dict[str, Tool], max_steps: int = 4) -> AgentResult:
    messages: list[dict] = [{"role": "system", "content": SYSTEM}, {"role": "user", "content": question}]
    schemas = [t.schema() for t in tools.values()]
    steps: list[Step] = []
    for _ in range(max_steps):
        reply = chat(messages, schemas)
        calls = parse_tool_calls(reply)
        if not calls:
            return AgentResult(answer=reply.strip(), steps=steps)
        messages.append(
            {
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {"type": "function", "function": {"name": c["name"], "arguments": c["arguments"]}}
                    for c in calls
                ],
            }
        )
        for c in calls:
            t0 = time.perf_counter()
            tool = tools.get(c["name"])
            ok = False
            if tool is None:
                result = f"Error: unknown tool {c['name']!r}. Available: {', '.join(tools)}."
            else:
                try:
                    result, ok = tool.fn(tool.args_model.model_validate(c["arguments"])), True
                except ValidationError as e:
                    result = f"Error: invalid arguments for {tool.name}: {e.errors()[0]['msg']}"
                except (ValueError, SyntaxError, ZeroDivisionError) as e:
                    result = f"Error: {e}"
            result = result[:1500]
            steps.append(
                Step(len(steps) + 1, c["name"], c["arguments"], result, ok, (time.perf_counter() - t0) * 1000)
            )
            log.info("step %d %s(%s) ok=%s", len(steps), c["name"], c["arguments"], ok)
            messages.append({"role": "tool", "name": c["name"], "content": result})
    return AgentResult(answer="I could not finish within the step limit.", steps=steps, stopped="max_steps")


def qwen_chat(generator, max_new_tokens: int = 200) -> ChatFn:
    """Adapter: a `Generator` (startupflow_ai.generate) as a tool-aware ChatFn."""
    import torch

    def chat(messages: list[dict], tools: list[dict]) -> str:
        prompt = generator.tokenizer.apply_chat_template(
            messages, tools=tools, tokenize=False, add_generation_prompt=True
        )
        inputs = generator.tokenizer(prompt, return_tensors="pt")
        with torch.inference_mode():
            out = generator.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=False,
                pad_token_id=generator.tokenizer.eos_token_id,
            )
        return generator.tokenizer.decode(out[0, inputs["input_ids"].shape[1] :], skip_special_tokens=True)

    return chat
