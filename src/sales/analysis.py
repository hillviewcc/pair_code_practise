"""Aggregations and reports over clean transactions."""

from datetime import date
from decimal import Decimal

from sales.models import Transaction


def deduplicate(transactions: list[Transaction]) -> list[Transaction]:
    """See TASKS.md, Task 3."""
    raise NotImplementedError


def filter_by_status(transactions: list[Transaction], status: str) -> list[Transaction]:
    """See TASKS.md, Task 4."""
    raise NotImplementedError


def filter_by_date_range(
    transactions: list[Transaction], start: date, end: date
) -> list[Transaction]:
    """See TASKS.md, Task 4."""
    raise NotImplementedError


def to_base_currency(amount: Decimal, currency: str, rates: dict[str, float]) -> Decimal:
    """See TASKS.md, Task 5."""
    raise NotImplementedError


def revenue_by_category(
    transactions: list[Transaction], rates: dict[str, float]
) -> dict[str, Decimal]:
    """See TASKS.md, Task 6."""
    raise NotImplementedError


def monthly_revenue(
    transactions: list[Transaction], rates: dict[str, float]
) -> dict[str, Decimal]:
    """See TASKS.md, Task 7."""
    raise NotImplementedError


def top_customers(
    transactions: list[Transaction], rates: dict[str, float], n: int = 3
) -> list[tuple[str, Decimal]]:
    """See TASKS.md, Task 8."""
    raise NotImplementedError
