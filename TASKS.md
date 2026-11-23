# Tasks

You are working on a small sales-reporting codebase. Raw transactions arrive as
`data/transactions.csv`; exchange rates are in `data/fx_rates.json`. The data is
**messy on purpose** — have a look at it before you start.

Work through the tasks in order. You are **not** expected to finish them all.
Talk through your thinking as you go, and write or run tests as you work.

Run the tests from the repo root with:

```bash
python -m unittest -v
```

Rules: Python standard library only. No third-party packages.

---

## Part A — Loading data (`src/sales/loader.py`)

### Task 1 — `parse_row`
Turn a single CSV row (a `dict[str, str]`) into a `Transaction`.

- `date` must be parsed from ISO format `YYYY-MM-DD` into a `datetime.date`.
- `quantity` → `int`, `unit_price` → `Decimal`.
- `status` and `currency` should be normalised to upper case.
- Raise `InvalidRowError` (with a helpful message) if **any** of the following:
  - a required field is missing or empty (`customer_id`, `quantity`, ...)
  - the date is not in `YYYY-MM-DD` format
  - quantity or unit price cannot be parsed
  - quantity is zero or negative

Some tests already exist in `tests/test_loader.py`. Make them pass, then add more.

### Task 2 — `load_transactions`
Read the whole CSV (use the provided `read_rows` helper) and return a tuple
`(valid_transactions, rejected_rows)`. Bad rows must **not** crash the load.

*Discussion:* how would you report *why* each row was rejected?

---

## Part B — Cleaning and filtering (`src/sales/analysis.py`)

### Task 3 — `deduplicate`
The file contains duplicate `transaction_id`s. Remove duplicates, keeping the
**first** occurrence and preserving the original order.

### Task 4 — `filter_by_status` and `filter_by_date_range`
- `filter_by_status` should be case-insensitive.
- `filter_by_date_range` is **inclusive** of both `start` and `end`.
  What should happen if `start > end`? Decide, implement, and test it.

---

## Part C — Aggregation (`src/sales/analysis.py`)

### Task 5 — `to_base_currency`
Convert an amount to GBP using the `rates` dict (`rate` = GBP per 1 unit of
currency). Round to 2 decimal places using banker's rounding *or* half-up —
pick one and justify it. Raise `ValueError` for an unknown currency.

### Task 6 — `revenue_by_category`
Return `{category: total_revenue_in_GBP}`, sorted by revenue **descending**.

### Task 7 — `monthly_revenue`
Return `{"YYYY-MM": total_revenue_in_GBP}` sorted by month ascending.

### Task 8 — `top_customers`
Return the top `n` customers by total GBP spend as a list of
`(customer_id, total)` tuples. Ties are broken by `customer_id` ascending.

---

## Part D — Testing and extension

### Task 9 — Tests for analysis
`tests/test_analysis.py` is mostly empty. Write tests for Tasks 3–8 using
small, hand-built `Transaction` objects (not the CSV). Think about edge cases:
empty input, a single item, ties, unknown currency.

### Task 10 — End to end
Get `python src/main.py` running and producing a sensible report.

### Task 11 — Stretch
Pick one:
- Write the cleaned, de-duplicated, GBP-converted data to `output/clean.csv`.
- Add a `rejections.csv` with the original row plus a `reason` column.
- Add support for the `DD/MM/YYYY` date format seen in one row.
- Add a command-line interface with `argparse` (`--status`, `--from`, `--to`).
