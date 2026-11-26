"""Fine-tune multilingual-e5-small as a 3-class query router, in plain PyTorch.

Run:  python router/train.py            (CPU, a few minutes)
Out:  results/router.json, results/router.md, models/router/ (gitignored)

Two models are compared on the same splits:
  baseline   frozen e5 embeddings -> logistic regression (only a linear layer trains)
  finetune   e5 encoder + linear head, all weights updated with AdamW

Architecture of `finetune`:
  tokens -> XLM-R encoder (12 layers, hidden 384) -> mean pool over non-pad tokens
         -> dropout -> Linear(384, 3) -> logits -> cross-entropy
"""

from __future__ import annotations

import json
import random
import time
from pathlib import Path

import numpy as np
import torch
from torch import nn
from transformers import AutoModel, AutoTokenizer, get_linear_schedule_with_warmup

AI_DIR = Path(__file__).resolve().parents[1]
DATA = AI_DIR / "data" / "router"
OUT = AI_DIR / "results"
MODEL_DIR = AI_DIR / "models" / "router"
BASE = "intfloat/multilingual-e5-small"
LABELS = ["memo_question", "out_of_domain", "prompt_injection"]
L2I = {lab: i for i, lab in enumerate(LABELS)}
SEED = 13


def set_seed(seed: int = SEED) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def load(split: str) -> tuple[list[str], torch.Tensor]:
    rows = [json.loads(x) for x in (DATA / f"{split}.jsonl").read_text(encoding="utf-8").splitlines()]
    return [f"query: {r['text']}" for r in rows], torch.tensor([L2I[r["label"]] for r in rows])


def mean_pool(hidden: torch.Tensor, mask: torch.Tensor) -> torch.Tensor:
    """Average token vectors, ignoring padding (mask=0)."""
    m = mask.unsqueeze(-1).float()
    return (hidden * m).sum(1) / m.sum(1).clamp(min=1e-9)


class Router(nn.Module):
    def __init__(self, base: str = BASE, n_labels: int = 3) -> None:
        super().__init__()
        self.encoder = AutoModel.from_pretrained(base)
        self.dropout = nn.Dropout(0.1)
        self.head = nn.Linear(self.encoder.config.hidden_size, n_labels)

    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor:
        h = self.encoder(input_ids=input_ids, attention_mask=attention_mask).last_hidden_state
        return self.head(self.dropout(mean_pool(h, attention_mask)))


def batches(texts, labels, tok, bs, shuffle):
    idx = list(range(len(texts)))
    if shuffle:
        random.shuffle(idx)
    for i in range(0, len(idx), bs):
        b = idx[i : i + bs]
        enc = tok([texts[j] for j in b], padding=True, truncation=True, max_length=64, return_tensors="pt")
        yield enc["input_ids"], enc["attention_mask"], labels[b]


@torch.inference_mode()
def predict(model: Router, tok, texts: list[str]) -> torch.Tensor:
    model.eval()
    preds = []
    for ids, mask, _ in batches(texts, torch.zeros(len(texts), dtype=torch.long), tok, 64, False):
        preds.append(model(ids, mask).argmax(-1))
    return torch.cat(preds)


def metrics(y: torch.Tensor, p: torch.Tensor) -> dict:
    y, p = y.numpy(), p.numpy()
    per = {}
    for i, lab in enumerate(LABELS):
        tp = int(((p == i) & (y == i)).sum())
        prec = tp / max(int((p == i).sum()), 1)
        rec = tp / max(int((y == i).sum()), 1)
        per[lab] = {"precision": prec, "recall": rec, "f1": 2 * prec * rec / max(prec + rec, 1e-9)}
    cm = [[int(((y == i) & (p == j)).sum()) for j in range(3)] for i in range(3)]
    return {
        "accuracy": float((y == p).mean()),
        "macro_f1": float(np.mean([v["f1"] for v in per.values()])),
        "per_class": per,
        "confusion": cm,
    }


# no_grad, not inference_mode: inference-mode tensors cannot be fed to a layer that is
# being trained (autograd refuses to save them for backward).
@torch.no_grad()
def embed_frozen(encoder, tok, texts: list[str]) -> torch.Tensor:
    out = []
    for ids, mask, _ in batches(texts, torch.zeros(len(texts), dtype=torch.long), tok, 64, False):
        out.append(nn.functional.normalize(mean_pool(encoder(ids, mask).last_hidden_state, mask), dim=-1))
    return torch.cat(out)


def train_baseline(tok, splits) -> dict:
    """Frozen encoder + logistic regression (a single Linear layer trained with full-batch Adam)."""
    set_seed()
    enc = AutoModel.from_pretrained(BASE).eval()
    feats = {k: embed_frozen(enc, tok, v[0]) for k, v in splits.items()}
    clf = nn.Linear(feats["train"].shape[1], 3)
    opt = torch.optim.Adam(clf.parameters(), lr=1e-2, weight_decay=1e-4)
    for _ in range(300):
        opt.zero_grad()
        loss = nn.functional.cross_entropy(clf(feats["train"]), splits["train"][1])
        loss.backward()
        opt.step()
    with torch.inference_mode():
        return {k: metrics(splits[k][1], clf(feats[k]).argmax(-1)) for k in splits if k != "train"}


def train_finetune(
    tok, splits, epochs: int = 8, lr: float = 3e-5, head_lr: float = 1e-3, bs: int = 16
) -> tuple[dict, list]:
    set_seed()
    model = Router()
    texts, labels = splits["train"]
    steps = epochs * ((len(texts) + bs - 1) // bs)
    # Run 1 used one lr (3e-5) for everything and collapsed to the majority class: the
    # randomly initialised head barely moved in 36 steps. Pretrained encoder weights need a
    # small lr (don't destroy them); the new head needs a large one.
    opt = torch.optim.AdamW(
        [
            {"params": model.encoder.parameters(), "lr": lr},
            {"params": model.head.parameters(), "lr": head_lr},
        ],
        weight_decay=0.01,
    )
    sched = get_linear_schedule_with_warmup(opt, int(0.1 * steps), steps)
    history, best_f1, best_state = [], -1.0, None
    for epoch in range(1, epochs + 1):
        model.train()
        t0, total, n = time.time(), 0.0, 0
        for ids, mask, y in batches(texts, labels, tok, bs, shuffle=True):
            loss = nn.functional.cross_entropy(model(ids, mask), y)
            opt.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step()
            sched.step()
            total, n = total + loss.item() * len(y), n + len(y)
        val = metrics(splits["val"][1], predict(model, tok, splits["val"][0]))
        history.append(
            {
                "epoch": epoch,
                "train_loss": total / n,
                "val_macro_f1": val["macro_f1"],
                "seconds": round(time.time() - t0, 1),
            }
        )
        print(history[-1])
        if val["macro_f1"] > best_f1:  # model selection on val only, never on test
            best_f1 = val["macro_f1"]
            best_state = {k: v.detach().clone() for k, v in model.state_dict().items()}
            history[-1]["selected"] = True
    model.load_state_dict(best_state)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    torch.save(model.state_dict(), MODEL_DIR / "router.pt")
    tok.save_pretrained(MODEL_DIR)
    res = {k: metrics(splits[k][1], predict(model, tok, splits[k][0])) for k in splits if k != "train"}
    return res, history


def main() -> None:
    torch.set_num_threads(8)
    tok = AutoTokenizer.from_pretrained(BASE)
    splits = {k: load(k) for k in ("train", "val", "test_heldout", "test_handwritten")}
    print({k: len(v[0]) for k, v in splits.items()})
    base = train_baseline(tok, splits)
    ft, history = train_finetune(tok, splits)
    result = {
        "baseline_frozen_logreg": base,
        "finetune": ft,
        "history": history,
        "sizes": {k: len(v[0]) for k, v in splits.items()},
    }
    OUT.mkdir(exist_ok=True)
    (OUT / "router.json").write_text(json.dumps(result, indent=2))
    lines = [
        "## Query router (3 classes), macro-F1 / accuracy",
        "",
        "| Split | n | Frozen e5 + LogReg | Fine-tuned e5 |",
        "|---|---|---|---|",
    ]
    for k in ("val", "test_heldout", "test_handwritten"):
        b, f = base[k], ft[k]
        lines.append(
            f"| {k} | {result['sizes'][k]} | {b['macro_f1']:.3f} / {b['accuracy']:.3f} "
            f"| {f['macro_f1']:.3f} / {f['accuracy']:.3f} |"
        )
    lines += [
        "",
        "Fine-tuned confusion matrix on test_handwritten (rows = true, cols = predicted; "
        + ", ".join(LABELS)
        + "):",
        "",
    ]
    lines += ["    " + str(row) for row in ft["test_handwritten"]["confusion"]]
    lines += ["", "| epoch | train loss | val macro-F1 | seconds |", "|---|---|---|---|"]
    lines += [
        f"| {h['epoch']} | {h['train_loss']:.4f} | {h['val_macro_f1']:.3f} | {h['seconds']} |"
        for h in history
    ]
    (OUT / "router.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
