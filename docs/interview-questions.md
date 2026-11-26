# 10 câu phỏng vấn AI Engineer Trainee có khả năng cao nhất cho project này

Mỗi câu gồm: ý chính cần nói, và chỗ trong repo để chứng minh. Hãy trả lời bằng **số đo thật** trong `ai/results/`.

---

### 1. "Walk me through your RAG pipeline."
- Ingestion: memo markdown → `normalize()` (NFC, bỏ ký tự điều khiển) → chunk (fixed 60 từ, overlap 15, có prefix tên công ty).
- Index: e5-small embed `passage:` → FAISS IndexFlatIP; song song BM25 tự viết.
- Query: embed `query:` + BM25 → RRF (k=60) → top-4 → gate → Qwen-0.5B trả JSON `{found, answer, citations}` → Pydantic validate → entity check + numeric check.
- File: `ai/startupflow_ai/pipeline.py` (đọc từ trên xuống là thấy toàn bộ luồng).

### 2. "Why hybrid search? Why RRF instead of adding scores?"
- BM25 và dense hỏng ở **các câu khác nhau**: không dấu (q06/q17) → BM25 thắng; cross-lingual (q32) → dense thắng. Hybrid là config duy nhất không có loại câu nào sụp.
- Điểm BM25 không bị chặn, cosine nằm ~0.8–0.9 → cộng trực tiếp vô nghĩa; RRF chỉ dùng thứ hạng nên không cần calibrate.
- Thừa nhận: trên tập này BM25 có Recall@1 cao nhất vì câu hỏi nêu tên công ty — trung thực về điều đó.

### 3. "How did you choose chunk size / strategy?"
- Bằng ablation, không phải cảm tính: fixed-60 > heading; chạy thêm fixed-30 để tách biến → **kích thước** quan trọng hơn ranh giới trên memo ngắn.
- Trade-off chung: chunk to → nhiều ngữ cảnh nhưng loãng & tốn token; chunk nhỏ → chính xác nhưng mất ngữ cảnh (tên công ty) → giải pháp: prefix tiêu đề.

### 4. "How do you evaluate a RAG system?"
- Tách **retrieval** (Recall@k, MRR — label = đúng memo + chứa evidence string, độc lập chiến lược chunking) và **generation** (accuracy, abstention đúng, citation precision, hallucination flags).
- Gold set 42 câu: 10 câu không có đáp án, câu tiếng Việt không dấu, cross-lingual, prompt injection.
- Điểm then chốt: evidence có trong top-4 ở 32/32 câu → lỗi còn lại nằm ở **generator**, không phải retrieval. Đó là lý do phải đo riêng hai tầng.

### 5. "Tell me about a failure you found and fixed." (câu chuyện mạnh nhất)
- v1: 16/32 câu bị "not found" sai. Đọc raw output → model **có** đáp án đúng nhưng ghi `citations` sai format (string, object, "passage numbers 1,2") → schema strict vứt bỏ.
- Fix: few-shot example + coerce citation + post-hoc attribution (gắn cờ `citations_inferred`), giữ nguyên nguyên tắc "không có nguồn thì không trả lời".
- Đo lại → so sánh v1/v2 trong README. Bài học: **đọc output thô trước khi đổ lỗi cho model**.

### 6. "How do you detect hallucinations?"
- Numeric check: mọi số trong câu trả lời phải xuất hiện trong passage được cite (xử lý `2,5`/`2.5`, `1.350`/`1350`).
- Entity check: hỏi về ShipNhanh mà cite memo HọcVui → abstain (bắt được q36, lỗi mà numeric check bỏ sót vì con số *có thật* — chỉ sai công ty).
- Giới hạn: lỗi ngữ nghĩa (q34 "giáo viên" ↔ "người biên soạn nội dung") cả hai check đều không bắt.

### 7. "What are the pitfalls of LLM-as-a-judge?"
- Judge 0.5B nói "supported" 17/18 lần → gần như luôn "yes" → vô dụng nếu không calibrate.
- Bias: độ dài, self-preference, position bias, nhạy prompt. Khắc phục: judge mạnh hơn generator, hỏi nhị phân theo từng claim, đo agreement với nhãn người.

### 8. "Explain tokenization and embeddings — what happens to 'VíXanh gọi vốn'?"
- SentencePiece: `▁Ví X an h ▁gọi ▁vốn` — âm tiết phổ biến là 1 token, tên hiếm bị băm nhỏ → dense yếu với tên riêng.
- Encoder 12 lớp → vector mỗi token → mean pooling (bỏ padding) → L2 normalize → cosine = dot product.
- Demo: `python ai/scripts/show_tokens.py`. Pitfall đo được: câu không liên quan vẫn cosine ~0.80 → không dùng cosine thô làm ngưỡng "liên quan".

### 9. "Show me you can train a model in PyTorch."
- Query router 3 lớp (memo / out-of-domain / injection): fine-tune e5-small + linear head, AdamW, linear warmup, grad clipping, mean pooling tự viết (`ai/router/train.py`).
- So sánh với baseline frozen embeddings + logistic regression → giải thích khi nào fine-tune đáng giá.
- **Chống leakage**: test dùng công ty khác + template khác + 30 câu viết tay; tách split *trước* khi upsample (bug mình đã tự bắt).
- Thừa nhận: dữ liệu sinh từ template → điểm cao trên test template không có nghĩa là tốt ngoài đời; tập viết tay là số đáng tin hơn.

### 10. "How would you serve this in production / make it faster?"
- Hiện tại: FastAPI, model load 1 lần (lifespan), timeout → 504, lock tuần tự hóa generate trên CPU, cache embedding query.
- Số đo: latency p50/p95 retrieval (cache on/off) và end-to-end trong README; generation chiếm >95% thời gian.
- Tiếp theo: vLLM (continuous batching, PagedAttention) trên GPU, quantization (int4/AWQ), streaming token, cache câu trả lời theo câu hỏi chuẩn hóa, ANN index (HNSW) khi > ~100k chunk, reranker chỉ trên top-20.

---

## Câu hỏi "bẫy" nên chuẩn bị
- *"Dataset của bạn là giả lập — kết quả có ý nghĩa gì?"* → Có ý nghĩa để so sánh tương đối giữa các config trên cùng tập; không khẳng định hiệu năng tuyệt đối. 1 câu = ~3 điểm Recall → sai số lớn.
- *"Threshold 0.80 chọn thế nào?"* → Từ sweep trên chính tập eval (không có held-out) — đó là hạn chế, đã ghi trong README.
- *"Tại sao không dùng LangChain?"* → Muốn hiểu và kiểm thử từng bước; framework hợp khi cần tích hợp nhanh nhiều nguồn/agent, và mình biết nó làm gì bên dưới.
- *"RAG hay fine-tune?"* → Kiến thức thay đổi thường xuyên + cần trích dẫn → RAG; fine-tune cho hành vi/định dạng (vd router, hoặc dạy model nhỏ xuất JSON chuẩn).
