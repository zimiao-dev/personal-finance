from models import Transaction

from repositories import (
    insert_transaction,
    find_transaction_by_id,
    find_all_transactions,
)


def test_insert_transaction_returns_id_and_persists_transaction(
    temporary_database,
):
    transaction = Transaction(
        id=None,
        amount=10.5,
        type="expense",
        category="food",
        transaction_date="2026-08-24",
        description="早餐",
    )

    inserted_id = insert_transaction(transaction)

    assert type(inserted_id) is int
    assert inserted_id > 0

    stored_transaction = find_transaction_by_id(inserted_id)

    assert stored_transaction is not None
    assert isinstance(stored_transaction, Transaction)

    assert inserted_id == stored_transaction.id

    assert stored_transaction.amount == 10.5
    assert stored_transaction.type == "expense"
    assert stored_transaction.category == "food"
    assert stored_transaction.transaction_date == "2026-08-24"
    assert stored_transaction.description == "早餐"


def test_find_transaction_by_id_returns_none_for_missing_id(
    temporary_database,
):
    transaction_id = 100

    transaction = find_transaction_by_id(transaction_id)

    assert transaction is None


def test_find_all_transactions_returns_empty_list_when_database_is_empty(
    temporary_database,
):
    result = find_all_transactions()

    assert result == []


def test_find_all_transactions_returns_transactions_in_descending_id_order(
    temporary_database,
):
    inserted_ids = []

    transaction1 = Transaction(
        id=None,
        amount=10.5,
        type="expense",
        category="food",
        transaction_date="2026-08-24",
        description="早餐",
    )

    transaction2 = Transaction(
        id=None,
        amount=14.5,
        type="expense",
        category="food",
        transaction_date="2026-08-24",
        description="午餐",
    )

    transaction3 = Transaction(
        id=None,
        amount=16.0,
        type="expense",
        category="food",
        transaction_date="2026-08-24",
        description="晚餐",
    )

    insert_transactions = [transaction1, transaction2, transaction3]

    for transaction in insert_transactions:
        inserted_id = insert_transaction(transaction)
        inserted_ids.append(inserted_id)

    found_transactions = find_all_transactions()

    found_ids = [transaction.id for transaction in found_transactions]

    assert found_ids == list(reversed(inserted_ids))


