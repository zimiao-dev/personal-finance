import pytest

from models import Transaction

from repositories import (
    insert_transaction,
    find_transaction_by_id,
    find_all_transactions,
    update_transaction,
    delete_transaction,
    query_transactions,
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


def test_update_transaction_updates_existing_transaction(
    temporary_database,
):
    transaction = Transaction(
        id=None,
        amount=10.5,
        type="income",
        category="clothes",
        transaction_date="2026-08-24",
        description="衣物",
    )

    inserted_id = insert_transaction(transaction)

    new_transaction = Transaction(
        id=inserted_id,
        amount=11.0,
        type="expense",
        category="food",
        transaction_date="2026-08-25",
        description="早餐",
    )

    affected_rows = update_transaction(new_transaction)

    assert affected_rows == 1

    updated_transaction = find_transaction_by_id(inserted_id)

    assert updated_transaction is not None
    assert updated_transaction.id == inserted_id
    assert updated_transaction.amount == new_transaction.amount
    assert updated_transaction.type == new_transaction.type
    assert updated_transaction.category == new_transaction.category
    assert updated_transaction.transaction_date == new_transaction.transaction_date
    assert updated_transaction.description == new_transaction.description


def test_update_transaction_returns_zero_for_missing_transaction(
    temporary_database,
):
    missing_id = 9999
    
    transaction = Transaction(
        id=missing_id,
        amount=10.5,
        type="expense",
        category="food",
        transaction_date="2026-08-24",
        description="早餐",
    )

    affected_rows = update_transaction(transaction)

    assert affected_rows == 0

    found_transaction = find_transaction_by_id(missing_id)

    assert found_transaction is None

    found_transactions = find_all_transactions()

    assert found_transactions == []


def test_delete_transaction_removes_existing_transaction(
    temporary_database,
):
    target_transaction = Transaction(
        id=None,
        amount=10.5,
        type="expense",
        category="food",
        transaction_date="2026-08-24",
        description="早餐",
    )

    unrelated_transaction = Transaction(
        id=None,
        amount=14.5,
        type="expense",
        category="food",
        transaction_date="2026-08-24",
        description="午餐",
    )

    target_id = insert_transaction(target_transaction)

    unrelated_id = insert_transaction(unrelated_transaction)

    affected_rows = delete_transaction(target_id)

    assert affected_rows == 1

    target_transaction = find_transaction_by_id(target_id)

    assert target_transaction is None

    unrelated_transaction = find_transaction_by_id(unrelated_id)

    assert unrelated_transaction is not None  


def test_delete_transaction_returns_zero_for_missing_transaction(
    temporary_database,
):
    unrelated_transaction = Transaction(
        id=None,
        amount=14.5,
        type="expense",
        category="food",
        transaction_date="2026-08-24",
        description="午餐",
    )

    unrelated_id = insert_transaction(unrelated_transaction)

    missing_id = 9999

    affected_rows = delete_transaction(missing_id)

    assert affected_rows == 0

    unrelated_transaction = find_transaction_by_id(unrelated_id)

    assert unrelated_transaction is not None 


def _insert_query_test_transactions():
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
        Transaction(
            id=None,
            amount=30.0,
            type="expense",
            category="food",
            transaction_date="2026-08-31",
            description="月末晚餐",
        ),
        Transaction(
            id=None,
            amount=5000.0,
            type="income",
            category="salary",
            transaction_date="2026-08-20",
            description="工资",
        ),
    ]

    inserted_ids = {
        "inside_food": insert_transaction(transactions[0]),
        "outside_after": insert_transaction(transactions[1]),
        "start_boundary": insert_transaction(transactions[2]),
        "inside_transport": insert_transaction(transactions[3]),
        "outside_before": insert_transaction(transactions[4]),
        "end_boundary": insert_transaction(transactions[5]),
        "inside_salary": insert_transaction(transactions[6]),
    }

    return inserted_ids


def test_query_transactions_filters_by_category(
    temporary_database,
):
    inserted_ids = _insert_query_test_transactions()

    queried_transactions = query_transactions(
        category="food",
    )

    queried_ids = [transaction.id for transaction in queried_transactions]

    expected_ids = [
        inserted_ids["end_boundary"],
        inserted_ids["outside_before"],
        inserted_ids["start_boundary"],
        inserted_ids["outside_after"],
        inserted_ids["inside_food"],
    ]

    assert queried_ids == expected_ids


def test_query_transactions_returns_empty_list_for_missing_category(
    temporary_database,
):
    _insert_query_test_transactions()

    missing_category = "medical"

    queried_transactions = query_transactions(
        category=missing_category,
    )

    assert queried_transactions == []


def test_query_transactions_filters_by_inclusive_date_range(
    temporary_database,
):
    inserted_ids = _insert_query_test_transactions()

    expected_ids = [
        inserted_ids["inside_salary"],
        inserted_ids["end_boundary"],
        inserted_ids["inside_transport"],
        inserted_ids["start_boundary"],
        inserted_ids["inside_food"],
    ]

    queried_transactions = query_transactions(
        start_date="2026-08-01", 
        end_date="2026-08-31",
    )

    queried_ids = [transaction.id for transaction in queried_transactions]

    assert queried_ids == expected_ids


def test_query_transactions_combines_category_and_date_range(
    temporary_database,
):
    inserted_ids = _insert_query_test_transactions()

    expected_ids = [
        inserted_ids["end_boundary"],
        inserted_ids["start_boundary"],
        inserted_ids["inside_food"],
    ]

    queried_transactions = query_transactions(
        category="food", 
        start_date="2026-08-01", 
        end_date="2026-08-31",
    )

    queried_ids = [transaction.id for transaction in queried_transactions]

    assert queried_ids == expected_ids


def test_query_transactions_returns_all_transactions_without_filters(
    temporary_database,
):
    inserted_ids = _insert_query_test_transactions()
    expected_ids = list(reversed(list(inserted_ids.values())))

    queried_transactions = query_transactions()
    queried_ids = [transaction.id for transaction in queried_transactions]
    
    assert queried_ids == expected_ids


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
def test_query_transactions_raises_value_error_when_only_one_date_is_provided(
    temporary_database,
    start_date,
    end_date,
):
    with pytest.raises(ValueError, match="开始日期和结束日期必须同时提供"):
        query_transactions(
            start_date=start_date, 
            end_date=end_date,
        )
