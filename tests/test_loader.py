import unittest
from datetime import date
from decimal import Decimal

from sales.loader import InvalidRowError, parse_row


def make_row(**overrides):
    row = {
        "transaction_id": "T9999",
        "date": "2024-01-03",
        "customer_id": "C001",
        "product": "Laptop",
        "category": "Electronics",
        "quantity": "2",
        "unit_price": "10.50",
        "currency": "gbp",
        "status": "completed",
    }
    row.update(overrides)
    return row


class TestParseRow(unittest.TestCase):
    def test_parses_valid_row(self):
        t = parse_row(make_row())
        self.assertEqual(t.transaction_id, "T9999")
        self.assertEqual(t.date, date(2024, 1, 3))
        self.assertEqual(t.quantity, 2)
        self.assertEqual(t.unit_price, Decimal("10.50"))
        self.assertEqual(t.total, Decimal("21.00"))

    def test_normalises_status_and_currency(self):
        t = parse_row(make_row())
        self.assertEqual(t.status, "COMPLETED")
        self.assertEqual(t.currency, "GBP")

    def test_missing_quantity_raises(self):
        with self.assertRaises(InvalidRowError):
            parse_row(make_row(quantity=""))

    def test_bad_price_raises(self):
        with self.assertRaises(InvalidRowError):
            parse_row(make_row(unit_price="abc"))

    # TODO: add tests for the remaining rules in TASKS.md Task 1
    # (bad date format, negative/zero quantity, missing customer_id, ...)


class TestLoadTransactions(unittest.TestCase):
    # TODO (Task 2): test load_transactions against a small temporary CSV.
    # Hint: tempfile.TemporaryDirectory or tempfile.NamedTemporaryFile.
    pass


if __name__ == "__main__":
    unittest.main()
