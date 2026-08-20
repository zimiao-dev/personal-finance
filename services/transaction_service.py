from models import Transaction
from repositories import (
    insert_transaction,
    find_all_transactions,
    find_transaction_by_id,
    update_transaction as update_transaction_repo,
    delete_transaction as delete_transaction_repo,
    query_transactions as query_transactions_repo
)


def add_transaction(transaction: Transaction) -> int:
    """
    添加交易记录
    """

    return insert_transaction(transaction)


def get_all_transactions() -> list[Transaction]:
    """
    查看所有的交易记录
    """

    return find_all_transactions()

def get_transaction_by_id(
        transaction_id: int
) -> Transaction | None:
    """
    根据ID获取交易记录
    """

    return find_transaction_by_id(transaction_id)


def update_transaction(transaction: Transaction) -> int:
    """
    修改交易记录
    """

    return update_transaction_repo(transaction)


def delete_transaction(transaction_id: int) -> int:
    """
    根据交易 id 删除交易记录
    """

    return delete_transaction_repo(transaction_id)


def query_transactions(
        category: str | None = None,
        start_date: str | None = None,
        end_date: str | None = None
) -> list[Transaction]:
    """
    按照日期或者分类查找账单
    """

    return query_transactions_repo(
        category,
        start_date,
        end_date
    )