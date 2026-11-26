## Query router (3 classes), macro-F1 / accuracy

| Split | n | Frozen e5 + LogReg | Fine-tuned e5 |
|---|---|---|---|
| val | 30 | 0.923 / 0.967 | 1.000 / 1.000 |
| test_heldout | 67 | 0.903 / 0.925 | 0.878 / 0.910 |
| test_handwritten | 30 | 0.899 / 0.900 | 0.789 / 0.800 |

Fine-tuned confusion matrix on test_handwritten (rows = true, cols = predicted; memo_question, out_of_domain, prompt_injection):

    [9, 1, 0]
    [0, 10, 0]
    [1, 4, 5]

| epoch | train loss | val macro-F1 | seconds |
|---|---|---|---|
| 1 | 1.0299 | 0.232 | 110.5 |
| 2 | 0.7598 | 0.232 | 92.9 |
| 3 | 0.4804 | 0.923 | 70.6 |
| 4 | 0.2463 | 1.000 | 94.9 |
| 5 | 0.1176 | 1.000 | 87.9 |
| 6 | 0.0685 | 1.000 | 80.3 |
| 7 | 0.0514 | 1.000 | 72.7 |
| 8 | 0.0451 | 1.000 | 62.7 |
