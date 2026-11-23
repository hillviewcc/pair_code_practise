"""Aggregations and reports over clean transactions."""

from collections import defaultdict
from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from sales.models import Transaction

PENNY = Decimal("0.01")


def deduplicate(transactions: list[Transaction]) -> list[Transaction]:
    """Drop repeated transaction_ids, keeping the first occurrence, in order."""
    seen: set[str] = set()
    result = []
    for t in transactions:
        if t.transaction_id not in seen:
            seen.add(t.transaction_id)
            result.append(t)
    return result


def filter_by_status(transactions: list[Transaction], status: str) -> list[Transaction]:
    """Case-insensitive status filter."""
    wanted = status.strip().upper()
    return [t for t in transactions if t.status.upper() == wanted]


def filter_by_date_range(
    transactions: list[Transaction], start: date, end: date
) -> list[Transaction]:
    """Transactions with start <= date <= end.

    Design choice: start > end is almost certainly a caller bug, so fail loudly
    rather than silently returning an empty list.
    """
    if start > end:
        raise ValueError(f"start {start} is after end {end}")
    return [t for t in transactions if start <= t.date <= end]


def to_base_currency(amount: Decimal, currency: str, rates: dict[str, float]) -> Decimal:
    """Convert to GBP and round half-up to pennies.

    Half-up is what most people (and most finance reports) expect: 0.125 -> 0.13.
    Banker's rounding (ROUND_HALF_EVEN) reduces bias over many sums and would
    also be defensible — the point is to choose deliberately.

    Decimal(str(rate)) avoids dragging float representation error into Decimal:
    Decimal(0.85) == 0.84999999999999997779553950749686919152736663818359375.
    """
    try:
        rate = rates[currency.upper()]
    except KeyError:
        raise ValueError(f"no FX rate for currency {currency!r}") from None
    return (amount * Decimal(str(rate))).quantize(PENNY, rounding=ROUND_HALF_UP)


def _gbp_total(t: Transaction, rates: dict[str, float]) -> Decimal:
    return to_base_currency(t.total, t.currency, rates)


def revenue_by_category(
    transactions: list[Transaction], rates: dict[str, float]
) -> dict[str, Decimal]:
    """{category: GBP revenue}, highest revenue first (ties: category name)."""
    totals: defaultdict[str, Decimal] = defaultdict(Decimal)
    for t in transactions:
        totals[t.category] += _gbp_total(t, rates)
    ordered = sorted(totals.items(), key=lambda item: (-item[1], item[0]))
    return dict(ordered)


def monthly_revenue(
    transactions: list[Transaction], rates: dict[str, float]
) -> dict[str, Decimal]:
    """{"YYYY-MM": GBP revenue}, oldest month first."""
    totals: defaultdict[str, Decimal] = defaultdict(Decimal)
    for t in transactions:
        totals[t.date.strftime("%Y-%m")] += _gbp_total(t, rates)
    # "YYYY-MM" strings sort chronologically as plain strings.
    return dict(sorted(totals.items()))


def top_customers(
    transactions: list[Transaction], rates: dict[str, float], n: int = 3
) -> list[tuple[str, Decimal]]:
    """Top n customers by GBP spend; ties broken by customer_id ascending."""
    if n < 0:
        raise ValueError("n must be non-negative")
    totals: defaultdict[str, Decimal] = defaultdict(Decimal)
    for t in transactions:
        totals[t.customer_id] += _gbp_total(t, rates)
    ranked = sorted(totals.items(), key=lambda item: (-item[1], item[0]))
    return ranked[:n]
