## Retrieval ablation (32 answerable questions)

| Config | #chunks | Recall@1 | Recall@3 | Recall@5 | MRR@10 |
|---|---|---|---|---|---|
| fixed+bm25_raw | 75 | 0.812 | 0.969 | 0.969 | 0.880 |
| fixed+bm25_fold | 75 | 0.844 | 0.938 | 0.969 | 0.886 |
| fixed+bm25_fold_bigram | 75 | 0.812 | 0.938 | 0.969 | 0.876 |
| fixed+dense | 75 | 0.750 | 0.875 | 1.000 | 0.844 |
| fixed+hybrid | 75 | 0.781 | 0.969 | 1.000 | 0.872 |
| fixed30+bm25_raw | 151 | 0.750 | 0.812 | 0.875 | 0.801 |
| fixed30+bm25_fold | 151 | 0.781 | 0.844 | 0.906 | 0.836 |
| fixed30+bm25_fold_bigram | 151 | 0.781 | 0.844 | 0.906 | 0.836 |
| fixed30+dense | 151 | 0.562 | 0.812 | 0.844 | 0.692 |
| fixed30+hybrid | 151 | 0.594 | 0.906 | 0.938 | 0.756 |
| heading+bm25_raw | 140 | 0.719 | 0.875 | 0.906 | 0.794 |
| heading+bm25_fold | 140 | 0.750 | 0.875 | 0.938 | 0.827 |
| heading+bm25_fold_bigram | 140 | 0.781 | 0.906 | 0.938 | 0.846 |
| heading+dense | 140 | 0.625 | 0.812 | 0.906 | 0.724 |
| heading+hybrid | 140 | 0.688 | 0.844 | 0.969 | 0.790 |

### Recall@3 by question type

| Config | crosslingual (n=4) | distractor (n=2) | factual (n=23) | no_diacritics (n=3) |
|---|---|---|---|---|
| fixed+bm25_raw | 0.75 | 1.00 | 1.00 | 1.00 |
| fixed+bm25_fold | 0.50 | 1.00 | 1.00 | 1.00 |
| fixed+bm25_fold_bigram | 0.50 | 1.00 | 1.00 | 1.00 |
| fixed+dense | 0.75 | 1.00 | 0.96 | 0.33 |
| fixed+hybrid | 0.75 | 1.00 | 1.00 | 1.00 |
| fixed30+bm25_raw | 0.25 | 0.50 | 0.96 | 0.67 |
| fixed30+bm25_fold | 0.25 | 0.50 | 0.96 | 1.00 |
| fixed30+bm25_fold_bigram | 0.25 | 0.50 | 0.96 | 1.00 |
| fixed30+dense | 0.25 | 1.00 | 0.96 | 0.33 |
| fixed30+hybrid | 0.75 | 1.00 | 1.00 | 0.33 |
| heading+bm25_raw | 0.50 | 1.00 | 0.96 | 0.67 |
| heading+bm25_fold | 0.25 | 1.00 | 0.96 | 1.00 |
| heading+bm25_fold_bigram | 0.50 | 1.00 | 0.96 | 1.00 |
| heading+dense | 0.75 | 1.00 | 0.87 | 0.33 |
| heading+hybrid | 0.50 | 1.00 | 0.96 | 0.33 |

### Abstention threshold sweep on top-1 dense cosine (fixed chunks)

| threshold | answerable kept | no-answer rejected |
|---|---|---|
| 0.78 | 1.00 | 0.00 |
| 0.79 | 1.00 | 0.10 |
| 0.80 | 1.00 | 0.10 |
| 0.81 | 0.97 | 0.10 |
| 0.82 | 0.97 | 0.10 |
| 0.83 | 0.97 | 0.20 |
| 0.84 | 0.94 | 0.40 |
| 0.85 | 0.91 | 0.40 |
| 0.86 | 0.88 | 0.50 |
| 0.87 | 0.75 | 0.60 |
| 0.88 | 0.66 | 0.80 |
| 0.89 | 0.62 | 0.90 |

### Abstention threshold sweep on top-1 dense cosine (fixed30 chunks)

| threshold | answerable kept | no-answer rejected |
|---|---|---|
| 0.78 | 1.00 | 0.00 |
| 0.79 | 1.00 | 0.00 |
| 0.80 | 1.00 | 0.10 |
| 0.81 | 0.97 | 0.10 |
| 0.82 | 0.97 | 0.10 |
| 0.83 | 0.97 | 0.10 |
| 0.84 | 0.94 | 0.20 |
| 0.85 | 0.88 | 0.30 |
| 0.86 | 0.81 | 0.50 |
| 0.87 | 0.72 | 0.70 |
| 0.88 | 0.72 | 0.70 |
| 0.89 | 0.62 | 0.80 |

### Abstention threshold sweep on top-1 dense cosine (heading chunks)

| threshold | answerable kept | no-answer rejected |
|---|---|---|
| 0.78 | 1.00 | 0.00 |
| 0.79 | 1.00 | 0.00 |
| 0.80 | 0.97 | 0.10 |
| 0.81 | 0.97 | 0.10 |
| 0.82 | 0.97 | 0.10 |
| 0.83 | 0.97 | 0.10 |
| 0.84 | 0.94 | 0.40 |
| 0.85 | 0.91 | 0.40 |
| 0.86 | 0.81 | 0.50 |
| 0.87 | 0.72 | 0.70 |
| 0.88 | 0.62 | 0.80 |
| 0.89 | 0.56 | 0.90 |
