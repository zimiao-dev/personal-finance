import pytest

from models import TransactionStatistics


@pytest.mark.parametrize(
    "total_income, total_expense, transaction_count",
    [
        (24.0, 12.0, 2),
        (12.0, 24.0, 2),
        (12.0, 12.0, 2),
    ],
    ids=[
        "positive_balance",
        "negative_balance",
        "zero_balance",
    ],
)
def test_transaction_statistics_calculates_balance(
    total_income,
    total_expense,
    transaction_count,
):
    statistics = TransactionStatistics(
        total_income=total_income,
        total_expense=total_expense,
        transaction_count=transaction_count,
    )

    assert statistics.balance == total_income - total_expense
