from database import get_connection


def get_statistics(
        start_date: str | None = None,
        end_date: str | None = None
):
    """
    获取收支统计原始数据
    """

    sql = """
    SELECT
        SUM(
            CASE
                WHEN type = 'income'
                THEN amount
                ELSE 0
            END
        ),
        SUM(
            CASE
                WHEN type = 'expense'
                THEN amount
                ELSE 0
            END
        )
    FROM transactions
    """

    params = []


    if start_date and end_date:

        sql += """
        WHERE transaction_date BETWEEN ? AND ?
        """

        params.append(start_date)
        params.append(end_date)


    with get_connection() as conn:

        cursor = conn.execute(
            sql,
            params
        )

        return cursor.fetchone()