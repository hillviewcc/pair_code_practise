"""Entry point: load the data and print a short report.

Run from the repo root:  python src/main.py
This will only work once the tasks are implemented.
"""

import json
from datetime import date
from pathlib import Path

from sales import analysis
from sales.loader import load_transactions

ROOT = Path(__file__).resolve().parent.parent


def main() -> None:
    transactions, rejected = load_transactions(ROOT / "data" / "transactions.csv")
    rates = json.loads((ROOT / "data" / "fx_rates.json").read_text())["rates"]

    print(f"Loaded {len(transactions)} transactions, rejected {len(rejected)} rows")

    clean = analysis.deduplicate(transactions)
    completed = analysis.filter_by_status(clean, "COMPLETED")
    print(f"{len(completed)} completed transactions after de-duplication")

    print("\nRevenue by category (GBP):")
    for category, total in analysis.revenue_by_category(completed, rates).items():
        print(f"  {category:<12} {total:>10.2f}")

    print("\nMonthly revenue (GBP):")
    for month, total in analysis.monthly_revenue(completed, rates).items():
        print(f"  {month}  {total:>10.2f}")

    print("\nTop customers (GBP):")
    for customer, total in analysis.top_customers(completed, rates, n=3):
        print(f"  {customer}  {total:>10.2f}")

    q1 = analysis.filter_by_date_range(completed, date(2024, 1, 1), date(2024, 3, 31))
    print(f"\nQ1 completed transactions: {len(q1)}")


if __name__ == "__main__":
    main()
