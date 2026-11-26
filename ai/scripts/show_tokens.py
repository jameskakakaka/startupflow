"""Show, step by step, how text becomes tokens and then a vector.

Run: python scripts/show_tokens.py "VíXanh gọi vốn bao nhiêu?"
"""

import sys

import numpy as np

from startupflow_ai.dense import Embedder

text = sys.argv[1] if len(sys.argv) > 1 else "VíXanh gọi vốn bao nhiêu?"
emb = Embedder("intfloat/multilingual-e5-small")
tok = emb.tokenizer

ids = tok(f"query: {text}")["input_ids"]
print("1) text       :", text)
print("2) subwords   :", tok.convert_ids_to_tokens(ids))
print("3) token ids  :", ids)
print(f"   ({len(ids)} tokens; '▁' marks a word start in SentencePiece; <s> and </s> are special tokens)")
vec = emb.embed_query(text, use_cache=False)
print(
    f"4) vector     : dim={vec.shape[0]}, L2 norm={np.linalg.norm(vec):.3f}, first 5={np.round(vec[:5], 3)}"
)

a = emb.embed_query("Vốn gọi của VíXanh", use_cache=False)
b = emb.embed_query("How much is VíXanh raising?", use_cache=False)
c = emb.embed_query("Thời tiết Hà Nội hôm nay", use_cache=False)
print("5) cosine(vi question, en paraphrase) =", round(float(a @ b), 3))
print("   cosine(vi question, unrelated vi)   =", round(float(a @ c), 3))
