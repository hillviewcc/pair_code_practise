"""Reading and parsing raw transaction data."""

import csv
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

from sales.models import Transaction


class InvalidRowError(ValueError):
    """Raised when a CSV row cannot be turned into a Transaction."""


REQUIRED_FIELDS = (
    "transaction_id",
    "date",
    "customer_id",
    "product",
    "category",
    "quantity",
    "unit_price",
    "currency",
    "status",
)


def parse_row(row: dict[str, str]) -> Transaction:
    """Convert one CSV row (as produced by csv.DictReader) into a Transaction."""
    # Strip whitespace once up front; treat None (short rows) as empty.
    cleaned = {key: (row.get(key) or "").strip() for key in REQUIRED_FIELDS}

    missing = [key for key, value in cleaned.items() if not value]
    if missing:
        raise InvalidRowError(f"missing required field(s): {', '.join(missing)}")

    try:
        # strptime is strict about the format, unlike date.fromisoformat in 3.11+,
        # which also accepts e.g. "20240103".
        parsed_date = datetime.strptime(cleaned["date"], "%Y-%m-%d").date()
    except ValueError:
        raise InvalidRowError(f"bad date {cleaned['date']!r}, expected YYYY-MM-DD") from None

    try:
        quantity = int(cleaned["quantity"])
    except ValueError:
        raise InvalidRowError(f"bad quantity {cleaned['quantity']!r}") from None
    if quantity <= 0:
        raise InvalidRowError(f"quantity must be positive, got {quantity}")

    try:
        unit_price = Decimal(cleaned["unit_price"])
    except InvalidOperation:
        raise InvalidRowError(f"bad unit_price {cleaned['unit_price']!r}") from None
    if not unit_price.is_finite() or unit_price < 0:
        raise InvalidRowError(f"unit_price must be a non-negative number, got {unit_price}")

    return Transaction(
        transaction_id=cleaned["transaction_id"],
        date=parsed_date,
        customer_id=cleaned["customer_id"],
        product=cleaned["product"],
        category=cleaned["category"],
        quantity=quantity,
        unit_price=unit_price,
        currency=cleaned["currency"].upper(),
        status=cleaned["status"].upper(),
    )


def load_transactions(path: str | Path) -> tuple[list[Transaction], list[dict[str, str]]]:
    """Load every row in the CSV at `path`.

    Returns (valid_transactions, rejected_rows). Each rejected row is a copy of
    the original row with an extra "reason" key explaining why it was rejected.
    """
    valid: list[Transaction] = []
    rejected: list[dict[str, str]] = []
    for row in read_rows(path):
        try:
            valid.append(parse_row(row))
        except InvalidRowError as exc:
            rejected.append({**row, "reason": str(exc)})
    return valid, rejected


def read_rows(path: str | Path) -> list[dict[str, str]]:
    """Helper: read the CSV into a list of dicts. Already implemented."""
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))
