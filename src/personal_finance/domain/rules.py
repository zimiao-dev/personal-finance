from datetime import date
from decimal import Decimal, DecimalException

from personal_finance.domain.enums import TransactionType
from personal_finance.domain.exceptions import DomainValidationError


MIN_TRANSACTION_AMOUNT = Decimal("0.0001")
MAX_TRANSACTION_AMOUNT = Decimal("99999999999.9999")
MAX_TRANSACTION_DECIMAL_PLACES = 4


def validate_transaction_id(value: object) -> int:
    if type(value) is not int or value <= 0:
        raise DomainValidationError("transaction ID must be a positive integer")

    return value


def validate_transaction_amount(value: object) -> Decimal:
    if type(value) is not Decimal:
        raise DomainValidationError("transaction amount must be a Decimal")

    if not value.is_finite():
        raise DomainValidationError("transaction amount must be finite")

    if value.as_tuple().exponent < -MAX_TRANSACTION_DECIMAL_PLACES:
        raise DomainValidationError("transaction amount has too many decimal places")

    if not MIN_TRANSACTION_AMOUNT <= value <= MAX_TRANSACTION_AMOUNT:
        raise DomainValidationError("transaction amount is out of range")

    return value


def normalize_category(value: object) -> str:
    if type(value) is not str:
        raise DomainValidationError("transaction category must be a string")

    normalized_value = value.strip()

    if normalized_value == "":
        raise DomainValidationError(
            "transaction category must be a non-empty string"
        )

    return normalized_value


def normalize_description(value: object) -> str | None:
    if value is None:
        return None

    if type(value) is not str:
        raise DomainValidationError(
            "transaction description must be a string"
        )

    normalized_value = value.strip()

    if normalized_value == "":
        return None

    return normalized_value


def validate_transaction_type(value: object) -> TransactionType:
    if type(value) is not TransactionType:
        raise DomainValidationError(
            "transaction type must be a TransactionType"
        )

    return value


def validate_transaction_date(value: object) -> date:
    if type(value) is not date:
        raise DomainValidationError("transaction date must be a date")

    return value


def validate_date_range(
    start_date: object,
    end_date: object,
) -> None:
    if start_date is None and end_date is None:
        return

    if start_date is None or end_date is None:
        raise DomainValidationError(
            "start_date and end_date must both be provided"
        )

    validated_start_date = validate_transaction_date(start_date)
    validated_end_date = validate_transaction_date(end_date)

    if validated_start_date > validated_end_date:
        raise DomainValidationError(
            "start_date must be less than or equal to end_date"
        )


def validate_statistics_total(value: object) -> Decimal:
    if type(value) is not Decimal:
        raise DomainValidationError(
            "statistics total must be a Decimal"
        )

    if not value.is_finite():
        raise DomainValidationError(
            "statistics total must be finite"
        )

    if value < 0:
        raise DomainValidationError(
            "statistics total must be non-negative"
        )

    return value


def validate_transaction_count(value: object) -> int:
    if type(value) is not int or value < 0:
        raise DomainValidationError(
            "transaction count must be a non-negative integer"
        )

    return value


def calculate_statistics_balance(
    total_income: Decimal,
    total_expense: Decimal,
) -> Decimal:
    try:
        balance = total_income - total_expense
    except DecimalException as exc:
        raise DomainValidationError(
            "statistics balance must be a finite Decimal"
        ) from exc

    if not balance.is_finite():
        raise DomainValidationError(
            "statistics balance must be a finite Decimal"
        )

    return balance
