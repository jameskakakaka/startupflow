## End-to-end answer evaluation (fixed+hybrid, top-4, Qwen2.5-0.5B-Instruct, CPU)

| Metric | Value |
|---|---|
| Answer accuracy, answerable (keyword match) | 15/32 = 0.47 |
| Evidence in top-4 context, answerable | 32/32 = 1.00 |
| False abstention, answerable | 16/32 = 0.50 |
| Correct abstention, no-answer | 8/10 = 0.80 |
| Citation precision (mean over answered) | 0.29 (n=16) |
| Answers flagged by numeric check | 0/18 |
| ...of which wrong by keyword | 0/0 |
| LLM-judge (0.5B) agreement with keyword label | 14/18 = 0.78 |
| LLM-judge said 'supported' | 17/18 |
| Latency when answering, p50 / max (ms) | 14808 / 49683 |
| Latency when abstaining, p50 (ms) | 36785 |

### By question type (answer accuracy or correct abstention)

| Type | n | Score |
|---|---|---|
| crosslingual | 4 | 0.50 |
| distractor | 2 | 0.50 |
| factual | 23 | 0.52 |
| no_answer | 10 | 0.80 |
| no_diacritics | 3 | 0.00 |
