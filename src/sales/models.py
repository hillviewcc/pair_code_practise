"""Domain model for a single sales transaction."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class Transaction:
    transaction_id: str
    date: date
    customer_id: str
    product: str
    category: str
    quantity: int
    unit_price: Decimal
    currency: str
    status: str

    @property
    def total(self) -> Decimal:
        """Line total in the transaction's own currency."""
        return self.unit_price * self.quantity
