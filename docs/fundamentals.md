# Fundamentals, explained through this project

Each section answers "what is it, where is it in this repo, and what trade-off did I make".

## 1. Tokenization

A transformer never sees characters. It sees **token ids** from a fixed vocabulary.
`multilingual-e5-small` uses a SentencePiece/XLM-R vocabulary (~250k subwords) shared
across ~100 languages. Run `python ai/scripts/show_tokens.py` to see it:

```
VíXanh gọi vốn bao nhiêu?
-> ['<s>', '▁que', 'ry', ':', '▁Ví', 'X', 'an', 'h', '▁gọi', '▁vốn', '▁bao', '▁nhiêu', '?', '</s>']
```

- `▁` marks the start of a word. Common Vietnamese syllables (`gọi`, `vốn`) are single
  tokens, while a rare brand name (`VíXanh`) is split into pieces. Rare names are
  therefore where dense models are weakest and BM25 is strongest.
- Token count, not character count, drives cost and latency, and it is what model
  context limits count.
- **Lexical** tokenization for BM25 (`ai/startupflow_ai/text.py`) is a different
  thing: a regex over Unicode letters, lower-cased, optionally accent-folded. Vietnamese
  is written as space-separated *syllables*, so `ví điện tử` gives 3 tokens for one
  word. A word segmenter (underthesea / pyvi) would be the principled fix. I tried
  syllable bigrams as a cheap approximation (`tokenize_with_bigrams`); the ablation
  table shows it does not reliably help on this corpus.

## 2. Unicode normalisation (Vietnamese-specific)

`ế` can be stored as one code point (NFC) or as `e` plus two combining marks (NFD). The
two forms look identical but `==` is false, so BM25 and exact-match checks miss.
`normalize()` converts every input, document and query to NFC (tested in
`ai/tests/test_core.py::test_nfc_makes_composed_and_decomposed_equal`).
`fold_diacritics()` maps `Tiền Nhanh` to `Tien Nhanh`, because many users type without
accents.

## 3. Embeddings

An embedding model maps text to a vector, here 384 numbers, such that texts with
similar meaning end up close together.
Pipeline: tokens → 12 transformer layers → one vector per token → **mean pooling** →
L2-normalise. With unit vectors, cosine similarity equals the dot product, so search is
just `matrix @ query` (`cosine_top_k` in `dense.py`). FAISS `IndexFlatIP` does the same
exact search. At scale you would swap it for an approximate index (IVF, HNSW) and
trade a little recall for speed.

E5 was trained with `query: ` / `passage: ` prefixes, so the code always adds them.
Observed pitfall: cosines are compressed. An unrelated sentence still scores ~0.80
(`show_tokens.py` output), so **raw cosine is a poor "is this relevant?" signal**. That
is why the abstention threshold barely works (see the README results).

## 4. Attention / Transformers (short)

Each layer lets every token build a weighted mix of all other tokens:
`softmax(QKᵀ/√d)·V`. Q, K and V are learned projections of the token vectors. The
weights say how much token *i* should look at token *j*. Several heads learn different
relations, and stacking layers builds context-dependent meaning: `vốn` (capital) next to
`gọi` (call/raise) means fundraising. The cost is O(n²) in sequence length, which is one
reason chunks are kept short.
Encoders (e5) see the whole input in both directions and are used to embed text.
Decoders (Qwen) use causal masking and generate one token at a time.

## 5. Chunking trade-offs

| Strategy | Pros | Cons |
|---|---|---|
| Fixed window + overlap (`fixed`, 60 words / 15 overlap) | simple, uniform size, overlap protects facts near boundaries | can mix two topics, can cut a sentence |
| Structure / heading (`heading`) | one coherent topic per chunk, clean citations | sizes vary; tiny sections carry little context |

The measured result surprised me. 60-word fixed chunks beat heading chunks. A 30-word
fixed run (`fixed30`), the same size as a typical section, showed that **chunk size,
not boundary placement**, explains most of the gap on these short memos. Both strategies
prefix each chunk with the company name. Without that prefix, a chunk like "raising
2.5M USD" would not say which company it belongs to.

## 6. BM25 vs dense vs hybrid

- **BM25** (`bm25.py`, written by hand) is exact term matching with IDF weighting and
  term-frequency saturation. It is great on names, numbers and accent-less queries, but
  it misses paraphrases and cross-lingual matches (an English question about a
  Vietnamese memo).
- **Dense** handles paraphrase and language mismatch, but it is weak on rare names and
  on accent-less Vietnamese. In the ablation, folded BM25 ranks both accent-less
  questions (q06, q17) 1st, while dense ranks them 4th with fixed chunks and misses both
  from the top 10 with heading chunks. Cross-lingual queries flip this: for q32 (an
  English question about a Vietnamese memo) BM25 finds nothing in the top 10, while
  dense ranks the evidence 2nd.
- **Hybrid (RRF)**: BM25 and cosine scores live on different scales, so we fuse
  *ranks*, `Σ 1/(60+rank)`, instead of scores. The result inherits each method's
  strengths. Recall@5 = 1.0 in the default config.

## 7. Re-ranking

A bi-encoder (e5) embeds the query and the document **separately**, which is fast
because document vectors are precomputed. A **cross-encoder** reads the query and the
chunk *together* and outputs one relevance score. It is more accurate but runs once per
candidate, so it is used only on the top 20–50 hits. It is **not run in this repo** (no
multilingual reranker under the agreed download budget). It is the next experiment,
because Recall@5 is already 1.0 while Recall@1 is ~0.78, and reordering the top 5 is
exactly what a reranker fixes.

## 8. Grounded generation and structured output

- The prompt numbers the passages `[1]..[n]` and marks them as *data, not instructions*
  (basic prompt-injection hygiene).
- The model must return JSON `{found, answer, citations}`. `parse_llm_answer` validates
  it with Pydantic, drops out-of-range citations, and downgrades "found but cites
  nothing" to not-found. On invalid JSON it retries once, then falls back to a safe
  "not found". The service never crashes on, or blindly trusts, model output.
- Greedy decoding makes evaluation reproducible.

## 9. Hallucination

A hallucination is a claim that the retrieved context does not support. It is checked
in two ways (`grounding.py`):
1. **Numeric check**: every number in the answer must appear in the cited passages,
   matching across `2,5` / `2.5` / `1.350` / `1350`. It is deterministic and cheap, and
   in finance wrong numbers are the most damaging failure.
2. **Sentence support**: each answer sentence is compared with the closest cited
   sentence by cosine. It is weak (it inherits the compressed-cosine problem), so it is
   reported, not used to block answers.

## 10. LLM-as-a-judge pitfalls

- A judge is just another model. Small judges are close to "always say yes" (measured
  here with the same 0.5B model; see the README).
- Known biases: favours longer answers, favours its own outputs (self-preference),
  position bias in pairwise comparison, and sensitivity to prompt wording.
- Mitigations: use a stronger model than the generator, ask binary per-claim questions,
  calibrate against a small **human-labelled** set and report agreement, and fix the
  prompt and temperature.

## 11. RAG vs fine-tuning

| | RAG | Fine-tuning (e.g. LoRA) |
|---|---|---|
| Adds **knowledge** that changes often | yes, re-index | no, retrain, and facts get blurred |
| Gives citations / traceability | yes | no |
| Changes **behaviour/format/style** | partly (prompt) | yes |
| Cost to update | minutes | GPU hours |

Deal memos change weekly and need citations, so this project uses RAG. Fine-tuning
would make sense for, e.g., a small intent classifier or for teaching the 0.5B model
the JSON format more reliably.
