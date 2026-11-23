# Solution notes

This is one reasonable answer, not the only one. Compare your approach, and
make sure you can *explain* any differences.

Compare with your attempt:

```bash
git diff attempt-1 solutions -- src tests
```

## Expected output of `python src/main.py`

```
Loaded 36 transactions, rejected 5 rows
29 completed transactions after de-duplication

Revenue by category (GBP):
  Electronics     5325.48
  Furniture       2377.73
  Stationery       207.07

Monthly revenue (GBP):
  2024-01     2752.85
  2024-02     2779.74
  2024-03     2377.69

Top customers (GBP):
  C010     1854.96
  C001     1314.96
  C002     1026.00

Q1 completed transactions: 29
```

The 5 rejected rows: T0009 (blank quantity), T0013 (price `abc`),
T0021 (negative quantity), T0028 (no customer), T0036 (`03/09/2024` date).
T0003 appears twice and is removed by `deduplicate`. T0012 has a lower-case
`completed` status and is still counted.

## Talking points the navigator may push on

- **Why `Decimal` not `float`?** Money. `0.1 + 0.2 != 0.3` in float.
  Also `Decimal(str(rate))` rather than `Decimal(rate)`, because a float rate
  carries its binary error into the Decimal.
- **Rounding:** half-up chosen (what people expect on an invoice). Half-even
  (banker's) is less biased across many sums. Also: round per line then sum,
  or sum then round? Per line matches how an invoice reads; say which you chose.
- **`strptime` vs `date.fromisoformat`:** in Python 3.11+ `fromisoformat`
  accepts `20240103` too, so `strptime("%Y-%m-%d")` is stricter.
- **`raise ... from None`** hides the noisy inner traceback. Use `from exc` if
  you want to keep the cause.
- **Rejected rows carry a `reason`:** answers the Task 2 discussion question
  without changing the return type.
- **`start > end`:** raising is a design choice (fail loudly on a caller bug).
  Returning `[]` is also defensible. Pick one, test it, say why.
- **Ties in sorting:** sort key `(-total, id)` gives a deterministic order.
- **Tests:** `subTest` for table-driven cases; `tempfile.TemporaryDirectory`
  plus `addCleanup` for file-based tests; small hand-built objects for unit tests.
- **Complexity:** everything is one pass O(n) plus an O(k log k) sort of groups.
  `deduplicate` uses a set for O(1) membership checks.
