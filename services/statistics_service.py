from models import TransactionStatistics

from repositories.statistics_repository import (
    get_statistics
)


def get_transaction_statistics(
        start_date=None,
        end_date=None
) -> TransactionStatistics:

    """
    收支统计
    """
    
    statistics = get_statistics(
        start_date,
        end_date
    )


    return TransactionStatistics(
        total_income=statistics["total_income"],
        total_expense=statistics["total_expense"]
    )