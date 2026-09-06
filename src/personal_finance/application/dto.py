from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from personal_finance.domain.enums import TransactionType
from personal_finance.domain.rules import (
    normalize_category,
    normalize_description,
    validate_date_range,
    validate_transaction_amount,
    validate_transaction_date,
    validate_transaction_type,
)


@dataclass(frozen=True)
class CreateTransactionData:
    amount: Decimal
    type: TransactionType
    category: str
    transaction_date: date
    description: str | None = None

    def __post_init__(self) -> None:
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
class ReplaceTransactionData:
    amount: Decimal
    type: TransactionType
    category: str
    transaction_date: date
    description: str | None

    def __post_init__(self) -> None:
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
class TransactionQuery:
    category: str | None = None
    start_date: date | None = None
    end_date: date | None = None

    def __post_init__(self) -> None:
        if self.category is not None:
            normalized_category = normalize_category(self.category)
            object.__setattr__(
                self,
                "category",
                normalized_category,
            )

        validate_date_range(self.start_date, self.end_date)


@dataclass(frozen=True)
class StatisticsQuery:
    start_date: date | None = None
    end_date: date | None = None

    def __post_init__(self) -> None:
        validate_date_range(self.start_date, self.end_date)
