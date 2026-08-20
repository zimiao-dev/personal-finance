from database import get_connection
from models import TransactionStatistics


def get_transaction_statistics(
        start_date: str | None = None,
        end_date: str | None = None
) -> TransactionStatistics:
    """
    收支统计
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

        row = cursor.fetchone()


        total_income = row[0] or 0

        total_expense = row[1] or 0


        return TransactionStatistics(
            total_income=total_income,
            total_expense=total_expense
        )