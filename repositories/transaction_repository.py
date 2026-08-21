from database import get_connection
from models import Transaction


def row_to_transaction(row) -> Transaction:
    """将数据库查询结果转换为 Transaction 对象"""

    return Transaction(
        id=row[0],
        amount=row[1],
        type=row[2],
        category=row[3],
        transaction_date=row[4],
        description=row[5]
    )


def insert_transaction(transaction: Transaction) -> int:
    """添加交易记录"""

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


def find_all_transactions() -> list[Transaction]:
    """查看所有的交易记录"""

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
        rows = conn.execute(sql).fetchall()
        return [row_to_transaction(row) for row in rows]


def update_transaction(transaction: Transaction) -> int:
    """修改交易记录"""

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
        cursor = conn.execute(
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


def find_transaction_by_id(transaction_id: int) -> Transaction | None:
    """根据 id 查找交易记录"""

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
        row = conn.execute(sql, (transaction_id,)).fetchone()

    if row is None:
        return None

    return row_to_transaction(row)


def delete_transaction(transaction_id: int) -> int:
    """根据交易 id 删除交易记录"""

    sql = """
    DELETE FROM transactions
    WHERE id=?;
    """

    with get_connection() as conn:
        cursor = conn.execute(sql, (transaction_id,))
        return cursor.rowcount


def query_transactions(
    category: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None
) -> list[Transaction]:
    """按照日期或者分类查找账单"""

    if (start_date is None) != (end_date is None):
        raise ValueError("开始日期和结束日期必须同时提供")

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
        sql += " AND category = ?"
        params.append(category)

    if start_date is not None:
        sql += " AND transaction_date BETWEEN ? AND ?"
        params.extend((start_date, end_date))

    sql += " ORDER BY id DESC;"

    with get_connection() as conn:
        rows = conn.execute(sql, params).fetchall()
        return [row_to_transaction(row) for row in rows]
