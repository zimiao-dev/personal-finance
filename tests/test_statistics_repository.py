import pytest

from models import Transaction
from repositories.statistics_repository import get_statistics
from repositories.transaction_repository import insert_transaction


def _insert_statistics_test_transactions():
    transactions = [
        Transaction(
            id=None,
            amount=1000.10,
            type="income",
            category="salary",
            transaction_date="2026-07-31",
            description="工资",
        ),
        Transaction(
            id=None,
            amount=10.10,
            type="expense",
            category="food",
            transaction_date="2026-08-01",
            description="早餐",
        ),
        Transaction(
            id=None,
            amount=120.25,
            type="income",
            category="bonus",
            transaction_date="2026-08-15",
            description="奖金",
        ),
        Transaction(
            id=None,
            amount=20.20,
            type="expense",
            category="transport",
            transaction_date="2026-08-20",
            description="地铁",
        ),
        Transaction(
            id=None,
            amount=30.35,
            type="income",
            category="salary",
            transaction_date="2026-08-31",
            description="工资",
        ),
        Transaction(
            id=None,
            amount=99.40,
            type="expense",
            category="food",
            transaction_date="2026-09-01",
            description="早餐",
        ),
    ]

    for transaction in transactions:
        insert_transaction(transaction)

    return transactions


def test_get_statistics_returns_zero_totals_for_empty_database(
    temporary_database,
):
    result = get_statistics()
    expected_income = 0
    expected_expense = 0
    expected_count = 0

    assert type(result) is dict

    assert set(result) == {
        "total_income",
        "total_expense",
        "transaction_count",
    }

    assert result["total_income"] == expected_income
    assert result["total_expense"] == expected_expense
    assert result["transaction_count"] == expected_count


def test_get_statistics_sums_income_only(
    temporary_database,
):
    transactions = [
        Transaction(
            id=None,
            amount=1000.10,
            type="income",
            category="salary",
            transaction_date="2026-07-31",
            description="工资",
        ),
        Transaction(
            id=None,
            amount=120.25,
            type="income",
            category="bonus",
            transaction_date="2026-08-15",
            description="奖金",
        ),
        Transaction(
            id=None,
            amount=30.35,
            type="income",
            category="salary",
            transaction_date="2026-08-31",
            description="工资",
        ),
    ]

    for transaction in transactions:
        insert_transaction(transaction)

    result = get_statistics()
    expected_income =  sum(transaction.amount for transaction in transactions)
    expected_expense = 0
    expected_count = len(transactions)

    assert result["total_income"] == pytest.approx(expected_income)
    assert result["total_expense"] == expected_expense
    assert result["transaction_count"] == expected_count


def test_get_statistics_sums_expense_only(
    temporary_database,
):
    transactions = [
        Transaction(
            id=None,
            amount=10.10,
            type="expense",
            category="food",
            transaction_date="2026-08-01",
            description="早餐",
        ),
        Transaction(
            id=None,
            amount=20.20,
            type="expense",
            category="transport",
            transaction_date="2026-08-20",
            description="地铁",
        ),
        Transaction(
            id=None,
            amount=99.40,
            type="expense",
            category="food",
            transaction_date="2026-09-01",
            description="早餐",
        ),
    ]

    for transaction in transactions:
        insert_transaction(transaction)

    result = get_statistics()
    expected_income = 0
    expected_expense = sum(transaction.amount for transaction in transactions)
    expected_count = len(transactions)

    assert result["total_income"] == expected_income
    assert result["total_expense"] == pytest.approx(expected_expense)
    assert result["transaction_count"] == expected_count


def test_get_statistics_separates_income_and_expense_totals(
    temporary_database,
):
    transactions = _insert_statistics_test_transactions()

    result = get_statistics()

    expected_income = sum(
        transaction.amount
        for transaction in transactions
        if transaction.type == "income"
    )

    expected_expense = sum(
        transaction.amount
        for transaction in transactions
        if transaction.type == "expense"
    )

    expected_count = len(transactions)

    assert result["total_income"] == pytest.approx(expected_income)
    assert result["total_expense"] == pytest.approx(expected_expense)
    assert result["transaction_count"] == expected_count


def test_get_statistics_filters_by_inclusive_date_range(
    temporary_database,
):
    start_date = "2026-08-01"
    end_date = "2026-08-31"

    transactions = _insert_statistics_test_transactions()

    result = get_statistics(
        start_date=start_date,
        end_date=end_date,
    )

    expected_income = sum(
        transaction.amount
        for transaction in transactions
        if start_date <= transaction.transaction_date <= end_date
        and transaction.type == "income"
    )

    expected_expense = sum(
        transaction.amount
        for transaction in transactions
        if start_date <= transaction.transaction_date <= end_date
        and transaction.type == "expense"
    )

    expected_count = sum(
        1
        for transaction in transactions
        if start_date <= transaction.transaction_date <= end_date
    )

    assert result["total_income"] == pytest.approx(expected_income)
    assert result["total_expense"] == pytest.approx(expected_expense)
    assert result["transaction_count"] == expected_count


def test_get_statistics_returns_zero_totals_when_date_range_has_no_matches(
    temporary_database,
):
    start_date = "2026-06-01"
    end_date = "2026-07-01"

    _insert_statistics_test_transactions()

    result = get_statistics(
        start_date=start_date,
        end_date=end_date,
    )

    expected_income = 0
    expected_expense = 0
    expected_count = 0

    assert result["total_income"] == expected_income
    assert result["total_expense"] == expected_expense
    assert result["transaction_count"] == expected_count


@pytest.mark.parametrize(
    "start_date, end_date",
    [
        ("2026-08-01", None),
        (None, "2026-08-31"),
    ],
    ids=[
        "start_date_only",
        "end_date_only",
    ],
)
def test_get_statistics_raises_value_error_when_only_one_date_is_provided(
    temporary_database,
    start_date,
    end_date,
):
    with pytest.raises(
        ValueError,
        match="开始日期和结束日期必须同时提供",
    ):
        get_statistics(
            start_date=start_date,
            end_date=end_date,
        )
