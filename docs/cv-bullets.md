# CV bullets: StartupFlow + Deal Memo Copilot

Mỗi số dưới đây đều được sinh ra bởi một script trong repo; cột "Nguồn" cho biết lệnh chạy. Nếu bạn chạy lại và ra số khác, hãy sửa bullet cho khớp.

## Bản đề xuất (AI Engineer Trainee)

**StartupFlow: Deal Memo Copilot** · *Python, PyTorch, Hugging Face, FAISS, FastAPI, Next.js, PostgreSQL*

- Built a bilingual (Vietnamese/English) RAG assistant over investment memos with hand-written BM25, multilingual-e5 dense retrieval (FAISS) and Reciprocal Rank Fusion. Hybrid search reached **Recall@5 = 1.00 / Recall@3 = 0.97** on a 42-question gold set, and a 15-config ablation showed BM25 and dense fail on different query types (accent-less vs cross-lingual).
- Designed an evaluation and failure-analysis loop (Recall@k, MRR, abstention, citation precision, numeric and entity hallucination checks). Raw-output inspection traced 16/32 false "not found" answers to malformed citations from a 0.5B LLM, and fixing parsing plus post-generation verification cut false abstentions **16 → 8**, exposing that a 0.5B judge rates 27/31 answers "supported" and is unreliable.
- Fine-tuned multilingual-e5-small in a hand-written PyTorch loop as a 3-class query router (in-domain / out-of-domain / prompt injection), diagnosed a majority-class collapse (fixed with per-group learning rates), and showed with company- and template-disjoint test sets that full fine-tuning overfits (macro-F1 **0.79** on hand-written queries) while a frozen-encoder linear probe generalises better (**0.90**).
- (optional) Built a framework-free tool-calling agent (RAG search, AST-sandboxed calculator, structured pipeline lookup) with Pydantic-validated arguments and step logs; on 8 tasks a 0.5B model selected the right tools 5/8 and answered 4/8, with failures traced to planning-without-acting and number transcription.

## Nguồn của từng số

| Số | Nguồn |
|---|---|
| Recall@5 1.00, Recall@3 0.97, 15 configs | `cd ai && python eval/run_retrieval_eval.py` → `ai/results/retrieval.md` (dòng `fixed+hybrid`) |
| 16/32 false abstention (v1) | `ai/results/answers_v1_baseline.md` |
| 8/32 (v3) | `python eval/replay_verification.py results/answers_v2.jsonl` → `ai/results/answers_v3_replay.txt` |
| 27/31 judge "supported" | `ai/results/answers_v2.md` |
| Agent 5/8, 4/8 | `cd ai && python eval/run_agent_eval.py` → `ai/results/agent.md` |
| Router 0.79 vs 0.90 | `cd ai && python router/train.py` → `ai/results/router.md` |

## Không được ghi
- "production", "scalable", "accuracy 95%", hay bất kỳ số nào không có trong bảng trên.
- Không ghi "answer accuracy" như một thành tích: 0.53 là thấp, nên hãy dùng nó làm câu chuyện failure analysis thay vì khoe.
- Phải nói rõ corpus là **synthetic** nếu được hỏi về dữ liệu.
