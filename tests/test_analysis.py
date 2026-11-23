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

    def test_empty(self):
        self.assertEqual(analysis.deduplicate([]), [])

    def test_no_duplicates_unchanged(self):
        items = [make_txn(transaction_id=f"T{i}") for i in range(5)]
        self.assertEqual(analysis.deduplicate(items), items)


class TestFilterByStatus(unittest.TestCase):
    def test_case_insensitive(self):
        a = make_txn(transaction_id="T1", status="COMPLETED")
        b = make_txn(transaction_id="T2", status="PENDING")
        self.assertEqual(analysis.filter_by_status([a, b], "completed"), [a])

    def test_no_match(self):
        self.assertEqual(analysis.filter_by_status([make_txn()], "REFUNDED"), [])


class TestFilterByDateRange(unittest.TestCase):
    def setUp(self):
        self.jan1 = make_txn(transaction_id="T1", date=date(2024, 1, 1))
        self.jan15 = make_txn(transaction_id="T2", date=date(2024, 1, 15))
        self.feb1 = make_txn(transaction_id="T3", date=date(2024, 2, 1))
        self.all = [self.jan1, self.jan15, self.feb1]

    def test_inclusive_bounds(self):
        result = analysis.filter_by_date_range(self.all, date(2024, 1, 1), date(2024, 1, 15))
        self.assertEqual(result, [self.jan1, self.jan15])

    def test_single_day(self):
        result = analysis.filter_by_date_range(self.all, date(2024, 2, 1), date(2024, 2, 1))
        self.assertEqual(result, [self.feb1])

    def test_start_after_end_raises(self):
        with self.assertRaises(ValueError):
            analysis.filter_by_date_range(self.all, date(2024, 2, 1), date(2024, 1, 1))


class TestToBaseCurrency(unittest.TestCase):
    def test_gbp_unchanged(self):
        self.assertEqual(analysis.to_base_currency(Decimal("12.34"), "GBP", RATES), Decimal("12.34"))

    def test_converts_and_rounds(self):
        # 89.00 EUR * 0.85 = 75.65
        self.assertEqual(analysis.to_base_currency(Decimal("89.00"), "EUR", RATES), Decimal("75.65"))
        # 129.00 USD * 0.79 = 101.91
        self.assertEqual(analysis.to_base_currency(Decimal("129.00"), "USD", RATES), Decimal("101.91"))

    def test_rounds_half_up(self):
        # 0.125 GBP -> 0.13 (half-even would give 0.12)
        self.assertEqual(analysis.to_base_currency(Decimal("0.125"), "GBP", RATES), Decimal("0.13"))

    def test_lowercase_currency_accepted(self):
        self.assertEqual(analysis.to_base_currency(Decimal("10"), "eur", RATES), Decimal("8.50"))

    def test_unknown_currency_raises(self):
        with self.assertRaises(ValueError):
            analysis.to_base_currency(Decimal("1"), "JPY", RATES)


class TestRevenueByCategory(unittest.TestCase):
    def test_sums_and_sorts_descending(self):
        txns = [
            make_txn(transaction_id="T1", category="A", unit_price=Decimal("5")),
            make_txn(transaction_id="T2", category="B", unit_price=Decimal("20")),
            make_txn(transaction_id="T3", category="A", unit_price=Decimal("10"), quantity=2),
        ]
        result = analysis.revenue_by_category(txns, RATES)
        self.assertEqual(list(result.items()), [("A", Decimal("25.00")), ("B", Decimal("20.00"))])

    def test_converts_currencies(self):
        txns = [make_txn(currency="EUR", unit_price=Decimal("100"))]
        self.assertEqual(analysis.revenue_by_category(txns, RATES), {"Misc": Decimal("85.00")})

    def test_empty(self):
        self.assertEqual(analysis.revenue_by_category([], RATES), {})


class TestMonthlyRevenue(unittest.TestCase):
    def test_groups_by_month_in_order(self):
        txns = [
            make_txn(transaction_id="T1", date=date(2024, 3, 5)),
            make_txn(transaction_id="T2", date=date(2024, 1, 31)),
            make_txn(transaction_id="T3", date=date(2024, 1, 1)),
            make_txn(transaction_id="T4", date=date(2023, 12, 31)),
        ]
        result = analysis.monthly_revenue(txns, RATES)
        self.assertEqual(
            list(result.items()),
            [
                ("2023-12", Decimal("10.00")),
                ("2024-01", Decimal("20.00")),
                ("2024-03", Decimal("10.00")),
            ],
        )


class TestTopCustomers(unittest.TestCase):
    def setUp(self):
        self.txns = [
            make_txn(transaction_id="T1", customer_id="C3", unit_price=Decimal("50")),
            make_txn(transaction_id="T2", customer_id="C1", unit_price=Decimal("30")),
            make_txn(transaction_id="T3", customer_id="C2", unit_price=Decimal("30")),
            make_txn(transaction_id="T4", customer_id="C4", unit_price=Decimal("5")),
        ]

    def test_top_n_with_tie_break(self):
        result = analysis.top_customers(self.txns, RATES, n=3)
        self.assertEqual(
            result,
            [("C3", Decimal("50.00")), ("C1", Decimal("30.00")), ("C2", Decimal("30.00"))],
        )

    def test_n_larger_than_customers(self):
        self.assertEqual(len(analysis.top_customers(self.txns, RATES, n=10)), 4)

    def test_n_zero(self):
        self.assertEqual(analysis.top_customers(self.txns, RATES, n=0), [])

    def test_aggregates_multiple_purchases(self):
        txns = self.txns + [make_txn(transaction_id="T5", customer_id="C4", unit_price=Decimal("100"))]
        self.assertEqual(analysis.top_customers(txns, RATES, n=1), [("C4", Decimal("105.00"))])


if __name__ == "__main__":
    unittest.main()
