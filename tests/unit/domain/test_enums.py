import pytest

from personal_finance.domain.enums import TransactionType


def test_transaction_type_exposes_supported_values() -> None:
    # Act + Assert
    assert TransactionType.INCOME.value == "income"
    assert TransactionType.EXPENSE.value == "expense"
    assert set(TransactionType) == {
        TransactionType.INCOME,
        TransactionType.EXPENSE,
    }


def test_transaction_type_constructs_from_supported_string() -> None:
    # Arrange
    income_value = "income"
    expense_value = "expense"

    # Act
    income_type = TransactionType(income_value)
    expense_type = TransactionType(expense_value)

    # Assert
    assert income_type is TransactionType.INCOME
    assert expense_type is TransactionType.EXPENSE


def test_transaction_type_rejects_unsupported_value() -> None:
    # Arrange
    unsupported_value = "transfer"

    # Act + Assert
    with pytest.raises(ValueError):
        TransactionType(unsupported_value)
