## End-to-end answer evaluation (fixed+hybrid, top-4, Qwen/Qwen2.5-0.5B-Instruct, CPU)

| Metric | Value |
|---|---|
| Answer accuracy, answerable (keyword match) | 17/32 = 0.53 |
| Evidence in top-4 context, answerable | 32/32 = 1.00 |
| False abstention, answerable | 6/32 = 0.19 |
| Correct abstention, no-answer | 5/10 = 0.50 |
| Citation precision (mean over answered) | 0.54 (n=26) |
| Citations inferred post-hoc | 10/31 |
| Abstained by entity check | 2 |
| Answers flagged by numeric check | 6/31 |
| ...of which wrong by keyword | 2/6 |
| LLM-judge (0.5B) agreement with keyword label | 15/31 = 0.48 |
| LLM-judge said 'supported' | 27/31 |
| Latency when answering, p50 / max (ms) | 16912 / 121039 |
| Latency when abstaining, p50 (ms) | 10790 |

### By question type (answer accuracy or correct abstention)

| Type | n | Score |
|---|---|---|
| crosslingual | 4 | 0.25 |
| distractor | 2 | 1.00 |
| factual | 23 | 0.61 |
| no_answer | 10 | 0.50 |
| no_diacritics | 3 | 0.00 |
