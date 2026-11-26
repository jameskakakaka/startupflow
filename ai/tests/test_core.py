"""Model-free unit tests for the core retrieval building blocks."""

import unicodedata

import numpy as np
import pytest

from startupflow_ai.bm25 import BM25
from startupflow_ai.chunking import Document, fixed_size_chunks, heading_chunks
from startupflow_ai.dense import cosine_top_k
from startupflow_ai.grounding import entity_mismatch, unsupported_numbers
from startupflow_ai.hybrid import rrf
from startupflow_ai.metrics import mrr, recall_at_k
from startupflow_ai.schemas import AskRequest, parse_llm_answer
from startupflow_ai.text import fold_diacritics, normalize, tokenize


def test_nfc_makes_composed_and_decomposed_equal():
    nfd = unicodedata.normalize("NFD", "Tiền Nhanh")
    assert nfd != "Tiền Nhanh"
    assert normalize(nfd) == "Tiền Nhanh"


def test_fold_diacritics():
    assert fold_diacritics("Đồng bằng sông Cửu Long") == "Dong bang song Cuu Long"
    assert tokenize("Ví Xanh gọi VỐN") == ["vi", "xanh", "goi", "von"]


DOC = Document(
    "acme",
    "Acme",
    "# Acme\n\n> synthetic\n\n## Team\n\nAlice and Bob.\n\n## Traction\n\n"
    + " ".join(f"w{i}" for i in range(100)),
)


def test_heading_chunks_one_per_section_with_title_prefix():
    chunks = heading_chunks(DOC)
    assert [c.section for c in chunks] == ["Team", "Traction"]
    assert chunks[0].text == "Acme | Team: Alice and Bob."


def test_fixed_chunks_overlap():
    chunks = fixed_size_chunks(DOC, size=40, overlap=10)
    first, second = chunks[0].text.split()[2:], chunks[1].text.split()[2:]
    assert first[-10:] == second[:10]
    with pytest.raises(ValueError):
        fixed_size_chunks(DOC, size=10, overlap=10)


def test_bm25_prefers_rare_matching_term():
    bm = BM25(["the cat sat", "the dog sat", "the the the"], tokenizer=str.split)
    assert bm.search("cat", k=3)[0][0] == 0
    assert bm.search("unknown", k=3) == []


def test_cosine_top_k_matches_bruteforce():
    rng = np.random.default_rng(0)
    m = rng.normal(size=(50, 8))
    m /= np.linalg.norm(m, axis=1, keepdims=True)
    q = m[7]
    assert cosine_top_k(q, m, 3)[0][0] == 7


def test_rrf_rewards_agreement():
    fused = rrf([[1, 2, 3], [2, 1, 4]])
    assert {fused[0][0], fused[1][0]} == {1, 2}
    assert fused[-1][0] in {3, 4}


def test_metrics():
    flags = [[False, True], [True, False], [False, False]]
    assert recall_at_k(flags, 1) == pytest.approx(1 / 3)
    assert recall_at_k(flags, 2) == pytest.approx(2 / 3)
    assert mrr(flags) == pytest.approx((0.5 + 1 + 0) / 3)


PASSAGES = ["Acme | Acme is raising 3 million USD.", "Beta | Beta has 40 employees."]


def test_parse_llm_answer_validates_and_filters_citations():
    ok = parse_llm_answer('noise {"found": true, "answer": "x", "citations": [1, 9]} tail', 3)
    assert ok and ok.citations == [1]
    assert parse_llm_answer("not json", 3) is None
    assert parse_llm_answer('{"found": "maybe"}', 3) is None
    # found=true with no valid or inferable citation is downgraded to not found
    assert parse_llm_answer('{"found": true, "answer": "x", "citations": [7]}', 3).found is False


@pytest.mark.parametrize(
    "raw",
    [
        '```json\n{"found": true, "answer": "Acme raises 3 million USD", "citations": ["[1]"]}\n```',
        '{"found": true, "answer": "Acme raises 3 million USD", "citations": [{"passage_number": 1}]}',
        '{"found": true, "answer": "Acme raises 3 million USD", "citations": ["Acme is raising 3 million"]}',
        '{"found": true, "answer": "Acme raises 3 million USD", "citations": [passage numbers 1]}',
    ],
)
def test_parse_repairs_common_small_model_citation_formats(raw):
    parsed = parse_llm_answer(raw, 2, PASSAGES)
    assert parsed and parsed.found and parsed.citations == [1] and not parsed.citations_inferred


def test_parse_infers_citation_from_numbers_when_missing():
    parsed = parse_llm_answer('{"found": true, "answer": "40 employees", "citations": []}', 2, PASSAGES)
    assert parsed.citations == [2] and parsed.citations_inferred


def test_entity_mismatch():
    titles = {"ShipNhanh", "HọcVui", "NôngTrại360"}
    assert entity_mismatch("Doanh thu của ShipNhanh?", ["HọcVui"], titles)
    assert not entity_mismatch("Doanh thu của ShipNhanh?", ["ShipNhanh"], titles)
    assert not entity_mismatch("nong trai 360 tiet kiem nuoc?", ["NôngTrại360"], titles)
    assert not entity_mismatch("Which startup does wage access?", ["HọcVui"], titles)


def test_unsupported_numbers_handles_vi_and_en_formats():
    ctx = "Doanh thu 1,8 tỷ đồng; disbursement 1,350 billion VND."
    assert unsupported_numbers("1.8 tỷ và 1350 tỷ", ctx) == []
    assert unsupported_numbers("2.5 million", ctx) == ["2.5"]


def test_ask_request_validation():
    assert AskRequest(question="  Ví  Xanh?  ").question == "Ví Xanh?"
    with pytest.raises(ValueError):
        AskRequest(question="  ")
    with pytest.raises(ValueError):
        AskRequest(question="x" * 501)
