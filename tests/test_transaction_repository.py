from models import Transaction

from repositories import( 
    insert_transaction,
    find_transaction_by_id,
)


def test_insert_transaction_returns_id_and_persists_transaction(temporary_database):
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
