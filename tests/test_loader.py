import csv
import tempfile
import unittest
from datetime import date
from decimal import Decimal
from pathlib import Path

from sales.loader import InvalidRowError, load_transactions, parse_row


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

    def test_strips_whitespace(self):
        t = parse_row(make_row(customer_id="  C001 ", quantity=" 2 "))
        self.assertEqual(t.customer_id, "C001")
        self.assertEqual(t.quantity, 2)

    def test_missing_quantity_raises(self):
        with self.assertRaises(InvalidRowError):
            parse_row(make_row(quantity=""))

    def test_bad_price_raises(self):
        with self.assertRaises(InvalidRowError):
            parse_row(make_row(unit_price="abc"))

    def test_missing_customer_raises_and_names_field(self):
        with self.assertRaisesRegex(InvalidRowError, "customer_id"):
            parse_row(make_row(customer_id=""))

    def test_absent_key_raises(self):
        row = make_row()
        del row["status"]
        with self.assertRaises(InvalidRowError):
            parse_row(row)

    def test_bad_date_formats_raise(self):
        for bad in ["03/01/2024", "2024/01/03", "20240103", "2024-13-01", "2024-02-30"]:
            with self.subTest(date=bad), self.assertRaises(InvalidRowError):
                parse_row(make_row(date=bad))

    def test_non_positive_quantity_raises(self):
        for bad in ["0", "-3"]:
            with self.subTest(quantity=bad), self.assertRaises(InvalidRowError):
                parse_row(make_row(quantity=bad))

    def test_non_integer_quantity_raises(self):
        with self.assertRaises(InvalidRowError):
            parse_row(make_row(quantity="1.5"))

    def test_nan_price_raises(self):
        with self.assertRaises(InvalidRowError):
            parse_row(make_row(unit_price="NaN"))


class TestLoadTransactions(unittest.TestCase):
    def write_csv(self, rows):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        path = Path(tmp.name) / "t.csv"
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(make_row().keys()))
            writer.writeheader()
            writer.writerows(rows)
        return path

    def test_splits_valid_and_rejected(self):
        path = self.write_csv(
            [
                make_row(transaction_id="T1"),
                make_row(transaction_id="T2", quantity="-1"),
                make_row(transaction_id="T3"),
            ]
        )
        valid, rejected = load_transactions(path)
        self.assertEqual([t.transaction_id for t in valid], ["T1", "T3"])
        self.assertEqual(len(rejected), 1)
        self.assertEqual(rejected[0]["transaction_id"], "T2")
        self.assertIn("quantity", rejected[0]["reason"])

    def test_empty_file(self):
        valid, rejected = load_transactions(self.write_csv([]))
        self.assertEqual((valid, rejected), ([], []))

    def test_real_data_file(self):
        path = Path(__file__).resolve().parent.parent / "data" / "transactions.csv"
        valid, rejected = load_transactions(path)
        # T0009 blank qty, T0013 bad price, T0021 negative qty,
        # T0028 no customer, T0036 DD/MM/YYYY date
        self.assertEqual(
            sorted(r["transaction_id"] for r in rejected),
            ["T0009", "T0013", "T0021", "T0028", "T0036"],
        )
        self.assertEqual(len(valid), 41 - 5)


if __name__ == "__main__":
    unittest.main()
