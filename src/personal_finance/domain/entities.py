from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from personal_finance.domain.enums import TransactionType
from personal_finance.domain.rules import (
    calculate_statistics_balance,
    normalize_category,
    normalize_description,
    validate_statistics_total,
    validate_transaction_amount,
    validate_transaction_count,
    validate_transaction_date,
    validate_transaction_id,
    validate_transaction_type,
)


@dataclass(frozen=True)
class Transaction:
    id: int
    amount: Decimal
    type: TransactionType
    category: str
    transaction_date: date
    description: str | None = None

    def __post_init__(self) -> None:
        validate_transaction_id(self.id)

        validate_transaction_amount(self.amount)

        validate_transaction_type(self.type)

        normalized_category = normalize_category(self.category)
        object.__setattr__(
            self,
            "category",
            normalized_category,
        )

        validate_transaction_date(self.transaction_date)

        normalized_description = normalize_description(self.description)
        object.__setattr__(
            self,
            "description",
            normalized_description,
        )


@dataclass(frozen=True)
class TransactionStatistics:
    total_income: Decimal = Decimal("0")
    total_expense: Decimal = Decimal("0")
    transaction_count: int = 0

    def __post_init__(self) -> None:
        validate_statistics_total(self.total_income)
        validate_statistics_total(self.total_expense)
        validate_transaction_count(self.transaction_count)

        calculate_statistics_balance(
            self.total_income,
            self.total_expense,
        )

    @property
    def balance(self) -> Decimal:
        return calculate_statistics_balance(
            self.total_income,
            self.total_expense,
        )
