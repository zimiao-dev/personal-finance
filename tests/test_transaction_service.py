import pytest

from models import Transaction
from services import transaction_service


def test_add_transaction_passes_transaction_and_returns_inserted_id(
    monkeypatch,
):
    transaction_id = 99
    transaction = Transaction(
        id=None,
        amount=10.5,
        type="expense",
        category="food",
        transaction_date="2026-08-24",
        description="早餐",
    )

    calls = []

    def fake_insert_transaction(received_transaction):
        calls.append(received_transaction)
        return transaction_id

    monkeypatch.setattr(
        transaction_service,
        "insert_transaction",
        fake_insert_transaction,
    )
    result = transaction_service.add_transaction(transaction)

    assert len(calls) == 1
    assert calls[0] is transaction
    assert type(result) is int
    assert result == transaction_id


def test_get_all_transactions_returns_repository_list_unchanged(
    monkeypatch,
):
    transactions = [
        Transaction(
            id=None,
            amount=18.5,
            type="expense",
            category="food",
            transaction_date="2026-08-15",
            description="工作餐",
        ),
        Transaction(
            id=None,
            amount=22.0,
            type="expense",
            category="food",
            transaction_date="2026-09-01",
            description="九月早餐",
        ),
        Transaction(
            id=None,
            amount=10.0,
            type="expense",
            category="food",
            transaction_date="2026-08-01",
            description="月初早餐",
        ),
        Transaction(
            id=None,
            amount=6.0,
            type="expense",
            category="transport",
            transaction_date="2026-08-10",
            description="地铁",
        ),
        Transaction(
            id=None,
            amount=12.0,
            type="expense",
            category="food",
            transaction_date="2026-07-31",
            description="七月晚餐",
        ),
    ]

    calls = []

    def fake_find_all_transactions():
        calls.append(True)
        return transactions

    monkeypatch.setattr(
        transaction_service,
        "find_all_transactions",
        fake_find_all_transactions,
    )

    result = transaction_service.get_all_transactions()

    assert calls == [True]
    assert result is transactions


@pytest.mark.parametrize(
    "transaction_id, repository_result",
    [
        (
            10,
            Transaction(
                id=10,
                amount=10.5,
                type="expense",
                category="food",
                transaction_date="2026-08-24",
                description="早餐",
            )
        ),
        (
            90,
            None
        ),
    ],
    ids=[
        "existing_transaction",
        "missing_transaction",
    ],
)
def test_get_transaction_by_id_passes_id_and_returns_repository_result(
    monkeypatch,
    transaction_id,
    repository_result,
):
    calls = []

    def fake_find_transaction_by_id(received_id):
        calls.append(received_id)
        return repository_result

    monkeypatch.setattr(
        transaction_service,
        "find_transaction_by_id",
        fake_find_transaction_by_id,
    )

    result = transaction_service.get_transaction_by_id(transaction_id)

    assert calls == [transaction_id]
    assert result is repository_result


def test_update_transaction_passes_transaction_and_returns_affected_rows(
    monkeypatch,
):
    transaction = Transaction(
        id=15,
        amount=10.5,
        type="expense",
        category="food",
        transaction_date="2026-08-24",
        description="早餐",
    )

    rowcount = 1
    calls = []

    def fake_update_transaction_repo(received_transaction):
        calls.append(received_transaction)
        return rowcount

    monkeypatch.setattr(
        transaction_service,
        "update_transaction_repo",
        fake_update_transaction_repo,
    )

    result = transaction_service.update_transaction(transaction)

    assert len(calls) == 1
    assert calls[0] is transaction
    assert result == rowcount


def test_delete_transaction_passes_id_and_returns_affected_rows(
    monkeypatch,
):
    transaction_id = 15
    rowcount = 1
    calls = []

    def fake_delete_transaction_repo(received_id):
        calls.append(received_id)
        return rowcount

    monkeypatch.setattr(
        transaction_service,
        "delete_transaction_repo",
        fake_delete_transaction_repo,
    )

    result = transaction_service.delete_transaction(transaction_id)

    assert calls == [transaction_id]
    assert result == rowcount


def test_query_transactions_passes_filters_and_returns_repository_list(
    monkeypatch,
):
    category = "food"
    start_date = "2026-08-01"
    end_date = "2026-08-20"

    transactions = [
        Transaction(
            id=None,
            amount=18.5,
            type="expense",
            category="food",
            transaction_date="2026-08-15",
            description="工作餐",
        ),
        Transaction(
            id=None,
            amount=22.0,
            type="expense",
            category="food",
            transaction_date="2026-08-10",
            description="八月早餐",
        ),
        Transaction(
            id=None,
            amount=10.0,
            type="expense",
            category="food",
            transaction_date="2026-08-01",
            description="月初早餐",
        ),
    ]

    calls = []

    def fake_query_transactions_repo(
        received_category,
        received_start_date,
        received_end_date,
    ):
        calls.append(
            (
                received_category,
                received_start_date,
                received_end_date,
            )
        )

        return transactions

    monkeypatch.setattr(
        transaction_service,
        "query_transactions_repo",
        fake_query_transactions_repo,
    )

    result = transaction_service.query_transactions(
        category=category,
        start_date=start_date,
        end_date=end_date,
    )

    assert calls == [(category, start_date, end_date)]
    assert result is transactions


def test_query_transactions_passes_none_filters_by_default(
    monkeypatch,
):
    transactions = [
        Transaction(
            id=None,
            amount=18.5,
            type="expense",
            category="food",
            transaction_date="2026-08-15",
            description="工作餐",
        ),
        Transaction(
            id=None,
            amount=22.0,
            type="expense",
            category="food",
            transaction_date="2026-09-01",
            description="九月早餐",
        ),
        Transaction(
            id=None,
            amount=10.0,
            type="expense",
            category="food",
            transaction_date="2026-08-01",
            description="月初早餐",
        ),
        Transaction(
            id=None,
            amount=6.0,
            type="expense",
            category="transport",
            transaction_date="2026-08-10",
            description="地铁",
        ),
        Transaction(
            id=None,
            amount=12.0,
            type="expense",
            category="food",
            transaction_date="2026-07-31",
            description="七月晚餐",
        ),
    ]

    calls = []

    def fake_query_transactions_repo(
        received_category,
        received_start_date,
        received_end_date,
    ):
        calls.append(
            (
                received_category,
                received_start_date,
                received_end_date,
            )
        )
        return transactions

    monkeypatch.setattr(
        transaction_service,
        "query_transactions_repo",
        fake_query_transactions_repo,
    )

    result = transaction_service.query_transactions()

    assert calls == [(None, None, None)]
    assert result is transactions


def test_query_transactions_propagates_repository_value_error(
    monkeypatch,
):
    error_message = "transaction repository sentinel error"

    def fake_query_transactions_repo(
        received_category,
        received_start_date,
        received_end_date,
    ):
        raise ValueError(error_message)

    monkeypatch.setattr(
        transaction_service,
        "query_transactions_repo",
        fake_query_transactions_repo,
    )

    with pytest.raises(
        ValueError,
        match=error_message,
    ):
        transaction_service.query_transactions()
