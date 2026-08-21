from database import get_connection


def get_statistics(
    start_date: str | None = None,
    end_date: str | None = None
) -> dict[str, float | int]:
    """获取收支统计原始数据"""

    if (start_date is None) != (end_date is None):
        raise ValueError("开始日期和结束日期必须同时提供")

    sql = """
    SELECT
        COALESCE(SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END), 0),
        COALESCE(SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END), 0),
        COUNT(*)
    FROM transactions
    """
    params = []

    if start_date is not None:
        sql += " WHERE transaction_date BETWEEN ? AND ?"
        params.extend((start_date, end_date))

    with get_connection() as conn:
        row = conn.execute(sql, params).fetchone()

    return {
        "total_income": row[0],
        "total_expense": row[1],
        "transaction_count": row[2]
    }
