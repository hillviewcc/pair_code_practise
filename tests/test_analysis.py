import unittest
from datetime import date
from decimal import Decimal

from sales import analysis
from sales.models import Transaction

RATES = {"GBP": 1.0, "EUR": 0.85, "USD": 0.79}


def make_txn(**overrides):
    fields = dict(
        transaction_id="T1",
        date=date(2024, 1, 1),
        customer_id="C1",
        product="Widget",
        category="Misc",
        quantity=1,
        unit_price=Decimal("10.00"),
        currency="GBP",
        status="COMPLETED",
    )
    fields.update(overrides)
    return Transaction(**fields)


class TestDeduplicate(unittest.TestCase):
    def test_keeps_first_occurrence(self):
        a = make_txn(transaction_id="T1", product="first")
        b = make_txn(transaction_id="T2")
        c = make_txn(transaction_id="T1", product="second")
        self.assertEqual(analysis.deduplicate([a, b, c]), [a, b])


# TODO (Task 9): add test classes for
#   filter_by_status, filter_by_date_range, to_base_currency,
#   revenue_by_category, monthly_revenue, top_customers


if __name__ == "__main__":
    unittest.main()
