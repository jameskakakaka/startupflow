"""Latency / throughput benchmark for the running API.

Run (server must be up):
  python eval/load_test.py --mode retrieval   # retrieval-only, cache off vs on
  python eval/load_test.py --mode http --n 20 --concurrency 2

`retrieval` mode measures the in-process retrieval step (embedding + FAISS +
BM25 + RRF) with the query-embedding cache disabled and then enabled, which
isolates what the cache buys. `http` mode measures end-to-end /ask latency,
including LLM generation, through FastAPI.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import statistics
import time
from pathlib import Path

import httpx

GOLD = Path(__file__).resolve().parents[1] / "data" / "eval" / "gold.jsonl"


def questions() -> list[str]:
    return [json.loads(x)["question"] for x in GOLD.read_text(encoding="utf-8").splitlines() if x.strip()]


def pctl(xs: list[float], p: float) -> float:
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(round(p / 100 * (len(xs) - 1))))]


def report(name: str, lat_ms: list[float], wall_s: float) -> dict:
    r = {
        "name": name,
        "n": len(lat_ms),
        "p50_ms": round(statistics.median(lat_ms), 1),
        "p95_ms": round(pctl(lat_ms, 95), 1),
        "throughput_rps": round(len(lat_ms) / wall_s, 2),
    }
    print(json.dumps(r))
    return r


def bench_retrieval(repeats: int) -> list[dict]:
    from startupflow_ai.config import Settings
    from startupflow_ai.pipeline import RAGPipeline

    pipe = RAGPipeline(Settings(), load_llm=False)
    qs = questions() * repeats
    out = []
    for use_cache in (False, True):
        pipe.embedder._cache.clear()
        lat = []
        t0 = time.perf_counter()
        for q in qs:
            t = time.perf_counter()
            pipe.retriever.search(q, 4, mode="hybrid", use_cache=use_cache)
            lat.append((time.perf_counter() - t) * 1000)
        out.append(
            report(f"retrieval hybrid, cache={'on' if use_cache else 'off'}", lat, time.perf_counter() - t0)
        )
    return out


async def bench_http(url: str, n: int, concurrency: int) -> dict:
    qs = (questions() * (n // 42 + 1))[:n]
    sem = asyncio.Semaphore(concurrency)
    lat: list[float] = []
    errors = 0

    async with httpx.AsyncClient(timeout=120) as client:

        async def one(q: str) -> None:
            nonlocal errors
            async with sem:
                t = time.perf_counter()
                r = await client.post(f"{url}/ask", json={"question": q})
                lat.append((time.perf_counter() - t) * 1000)
                errors += r.status_code != 200

        t0 = time.perf_counter()
        await asyncio.gather(*(one(q) for q in qs))
        wall = time.perf_counter() - t0
    r = report(f"http /ask, concurrency={concurrency}, errors={errors}", lat, wall)
    r["errors"] = errors
    return r


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["retrieval", "http"], default="retrieval")
    ap.add_argument("--url", default="http://127.0.0.1:8000")
    ap.add_argument("--n", type=int, default=20)
    ap.add_argument("--concurrency", type=int, default=1)
    ap.add_argument("--repeats", type=int, default=5)
    a = ap.parse_args()
    if a.mode == "retrieval":
        bench_retrieval(a.repeats)
    else:
        asyncio.run(bench_http(a.url, a.n, a.concurrency))


if __name__ == "__main__":
    main()
