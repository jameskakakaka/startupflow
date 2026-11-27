## Tool-calling agent (Qwen/Qwen2.5-0.5B-Instruct, CPU, max 4 steps), 8 tasks

- Tool selection correct: 5/8
- Final answer correct: 4/8
- Invalid tool calls (unknown tool / bad args): 1 of 5 calls

| id | question | expected tools | used tools | tool ok | answer ok | s |
|---|---|---|---|---|---|---|
| a1 | Which startups are in Due Diligence? | list_startups | list_startups | ✅ | ✅ | 20.4 |
| a2 | Startup nào đang ở trạng thái Passed? | list_startups | list_startups | ✅ | ✅ | 13.9 |
| a3 | List the Seed-stage startups that are in Reviewing. | list_startups | list_startups | ✅ | ✅ | 13.6 |
| a4 | VíXanh đang gọi vốn bao nhiêu? | search_memos | (none) | ❌ | ❌ | 7.5 |
| a5 | What is 15% of 96 billion VND? Answer in billion VND. | calculator | calculator | ✅ | ❌ | 12.7 |
| a6 | How much are PayNest and CareLink raising in total, in million USD? | search_memos, calculator | (none) | ❌ | ❌ | 10.7 |
| a7 | What is SoKa Lend's NPL ratio multiplied by 2? | search_memos, calculator | calculator | ❌ | ❌ | 11.7 |
| a8 | What's the weather in Hanoi today? | (none) | (none) | ✅ | ✅ | 8.3 |
