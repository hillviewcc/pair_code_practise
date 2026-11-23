"""Reading and parsing raw transaction data."""

import csv
from pathlib import Path

from sales.models import Transaction


class InvalidRowError(ValueError):
    """Raised when a CSV row cannot be turned into a Transaction."""


def parse_row(row: dict[str, str]) -> Transaction:
    """Convert one CSV row (as produced by csv.DictReader) into a Transaction.

    See TASKS.md, Task 1.
    """
    raise NotImplementedError


def load_transactions(path: str | Path) -> tuple[list[Transaction], list[dict[str, str]]]:
    """Load every row in the CSV at `path`.

    Returns (valid_transactions, rejected_rows).

    See TASKS.md, Task 2.
    """
    raise NotImplementedError


def read_rows(path: str | Path) -> list[dict[str, str]]:
    """Helper: read the CSV into a list of dicts. Already implemented."""
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))
