from database import get_connection
from models import Transaction


def add_transaction(transaction: Transaction) -> int:
    """
    添加交易记录
    """

    sql = """
    INSERT INTO transactions
    (
        amount,
        type,
        category,
        transaction_date,
        description
    )
    VALUES (?, ?, ?, ?, ?)
    """

    with get_connection() as conn:

        cursor = conn.execute(
            sql,
            (
                transaction.amount,
                transaction.type,
                transaction.category,
                transaction.transaction_date,
                transaction.description
            )
        )

        return cursor.lastrowid