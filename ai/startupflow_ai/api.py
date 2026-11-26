"""FastAPI service: POST /ask, GET /health.

Run:  uvicorn startupflow_ai.api:app --port 8000

- Models load once at startup (lifespan), not per request.
- The CPU-bound pipeline runs in a worker thread and is wrapped in a timeout,
  so a slow generation returns 504 instead of hanging the client.
- One lock serialises generation: a single CPU model gains nothing from
  concurrent generate() calls, and serialising keeps memory bounded.
"""

from __future__ import annotations

import asyncio
import logging
import threading
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException

from startupflow_ai.config import Settings
from startupflow_ai.pipeline import RAGPipeline
from startupflow_ai.schemas import AskRequest, AskResponse

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("startupflow_ai.api")

state: dict = {}
_gen_lock = threading.Lock()


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = Settings()
    pipe = RAGPipeline(settings)
    _ = pipe.generator  # warm the LLM so the first request is not slow
    state.update(pipe=pipe, settings=settings, started=time.time())
    log.info("ready: chunking=%s retrieval=%s", settings.chunking, settings.retrieval)
    yield
    state.clear()


app = FastAPI(title="StartupFlow Deal Memo Copilot", version="0.1.0", lifespan=lifespan)


@app.get("/health")
def health() -> dict:
    pipe: RAGPipeline | None = state.get("pipe")
    return {
        "status": "ok" if pipe else "loading",
        "chunks": len(pipe.chunks) if pipe else 0,
        "query_cache_hits": pipe.embedder.cache_hits if pipe else 0,
    }


def _ask_sync(req: AskRequest) -> AskResponse:
    with _gen_lock:
        return state["pipe"].ask(req.question, top_k=req.top_k)


@app.post("/ask", response_model=AskResponse)
async def ask(req: AskRequest) -> AskResponse:
    if "pipe" not in state:
        raise HTTPException(503, "model is loading")
    timeout = state["settings"].request_timeout_s
    t0 = time.perf_counter()
    try:
        resp = await asyncio.wait_for(asyncio.to_thread(_ask_sync, req), timeout=timeout)
    except TimeoutError as exc:
        log.warning("timeout after %.0fs: %r", timeout, req.question[:80])
        raise HTTPException(504, "generation timed out") from exc
    except Exception as exc:  # never leak internals to the client
        log.exception("ask failed")
        raise HTTPException(500, "internal error") from exc
    log.info(
        "ask found=%s grounded=%s total=%.0fms q=%r",
        resp.found,
        resp.grounded,
        (time.perf_counter() - t0) * 1000,
        req.question[:80],
    )
    return resp
