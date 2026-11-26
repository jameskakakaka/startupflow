## Query router (3 classes), macro-F1 / accuracy

| Split | n | Frozen e5 + LogReg | Fine-tuned e5 |
|---|---|---|---|
| val | 30 | 0.923 / 0.967 | 0.232 / 0.533 |
| test_heldout | 67 | 0.903 / 0.925 | 0.326 / 0.612 |
| test_handwritten | 30 | 0.899 / 0.900 | 0.232 / 0.367 |

Fine-tuned confusion matrix on test_handwritten (rows = true, cols = predicted; memo_question, out_of_domain, prompt_injection):

    [10, 0, 0]
    [9, 1, 0]
    [10, 0, 0]

| epoch | train loss | val macro-F1 | seconds |
|---|---|---|---|
| 1 | 1.0201 | 0.237 | 102.7 |
| 2 | 0.7966 | 0.232 | 70.8 |
| 3 | 0.6837 | 0.232 | 97.2 |
