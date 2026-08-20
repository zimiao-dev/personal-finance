from models import TransactionStatistics

from repositories.statistics_repository import (
    get_statistics
)


def get_transaction_statistics(
        start_date=None,
        end_date=None
):

    """
    收支统计
    """
    
    row = get_statistics(
        start_date,
        end_date
    )


    total_income = row[0] or 0

    total_expense = row[1] or 0


    return TransactionStatistics(
        total_income=total_income,
        total_expense=total_expense
    )