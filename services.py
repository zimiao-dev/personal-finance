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
    VALUES (?, ?, ?, ?, ?);
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


def get_all_transactions() -> list[Transaction]:
    """
    查看所有的交易记录
    """

    sql = """
    SELECT
        id,
        amount,
        type,
        category,
        transaction_date,
        description
    FROM transactions
    ORDER BY id DESC;
    """

    with get_connection() as conn:

        cursor = conn.cursor()

        cursor.execute(sql)

        rows = cursor.fetchall()

        transactions = []

        for row in rows:

            transaction = Transaction(
                id=row[0],
                amount=row[1],
                type=row[2],
                category=row[3],
                transaction_date=row[4],
                description=row[5]
            )

            transactions.append(transaction)

        return transactions


def update_transaction(transaction: Transaction) -> int:
    """
    修改交易记录
    """

    sql = """
    UPDATE transactions
    SET
        amount=?,
        type=?,
        category=?,
        transaction_date=?,
        description=?
    WHERE id=?;
    """

    with get_connection() as conn:

        cursor = conn.cursor()

        cursor.execute(
            sql,
            (
                transaction.amount,
                transaction.type,
                transaction.category,
                transaction.transaction_date,
                transaction.description,
                transaction.id
            )
        )

        return cursor.rowcount
