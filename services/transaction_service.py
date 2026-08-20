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


def get_transaction_by_id(transaction_id: int) -> Transaction | None:
    """
    根据 id 查找交易记录
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
    WHERE id=?;
    """

    with get_connection() as conn:

        cursor = conn.execute(
            sql,
            (transaction_id,)
        )

        row = cursor.fetchone()

        if row is None:
            return None

        transaction = Transaction(
            id=row[0],
            amount=row[1],
            type=row[2],
            category=row[3],
            transaction_date=row[4],
            description=row[5]
        )

        return transaction


def delete_transaction(transaction_id: int) -> int:
    """
    根据交易 id 删除交易记录
    """
    sql = """
    DELETE FROM transactions
    WHERE id=?;
    """

    with get_connection() as conn:
        cursor = conn.execute(
            sql,
            (transaction_id,)
        )

        return cursor.rowcount


def query_transactions(
        category: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None
) -> list[Transaction]:
    """
    按照日期或者分类查找账单
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
    WHERE 1=1
    """

    params = []


    if category:
        sql += """
        AND category = ?
        """
        params.append(category)


    if start_date and end_date:
        sql += """
        AND transaction_date BETWEEN ? AND ?
        """
        params.append(start_date)
        params.append(end_date)


    sql += """
    ORDER BY id DESC;
    """


    with get_connection() as conn:

        cursor = conn.execute(
            sql,
            params
        )

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