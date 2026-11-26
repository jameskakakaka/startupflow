"""API contract tests with a stub pipeline (no models are loaded)."""

import time

from fastapi.testclient import TestClient

from startupflow_ai import api
from startupflow_ai.config import Settings
from startupflow_ai.schemas import AskResponse


class StubPipe:
    chunks = [object()] * 3

    class embedder:  # noqa: N801
        cache_hits = 0

    def __init__(self, delay: float = 0.0):
        self.delay = delay

    def ask(self, question, top_k=None):
        time.sleep(self.delay)
        return AskResponse(
            found=True,
            answer=f"echo: {question}",
            citations=[1],
            sources=[],
            grounded=True,
            unsupported_numbers=[],
            timings_ms={},
        )


def client(delay=0.0, timeout=5.0) -> TestClient:
    api.state.clear()
    api.state.update(pipe=StubPipe(delay), settings=Settings(request_timeout_s=timeout))
    return TestClient(api.app)  # not used as a context manager -> lifespan (model loading) is skipped


def test_health():
    assert client().get("/health").json()["status"] == "ok"


def test_ask_normalises_question():
    r = client().post("/ask", json={"question": "  Ví   Xanh? "})
    assert r.status_code == 200
    assert r.json()["answer"] == "echo: Ví Xanh?"


def test_ask_rejects_invalid_input():
    c = client()
    assert c.post("/ask", json={"question": ""}).status_code == 422
    assert c.post("/ask", json={"question": "x" * 600}).status_code == 422
    assert c.post("/ask", json={"question": "ok?", "top_k": 50}).status_code == 422


def test_ask_times_out_with_504():
    r = client(delay=0.5, timeout=0.1).post("/ask", json={"question": "slow question"})
    assert r.status_code == 504
