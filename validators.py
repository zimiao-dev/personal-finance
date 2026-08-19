from datetime import datetime


def validate_amount(amount: str) -> float:
    """
    校验金额
    """

    try:
        amount = float(amount)

    except ValueError:
        raise ValueError(
            "金额必须为数字"
        )


    if amount <= 0:
        raise ValueError(
            "金额必须大于0"
        )

    return amount



def validate_date(date_str: str) -> str:
    """
    校验日期格式
    """

    try:
        datetime.strptime(
            date_str,
            "%Y-%m-%d"
        )

    except ValueError:
        raise ValueError(
            "日期格式错误，应为 YYYY-MM-DD"
        )


    return date_str



def validate_type(transaction_type: str) -> str:
    """
    校验交易类型
    """

    transaction_type = transaction_type.lower()


    if transaction_type not in [
        "income",
        "expense"
    ]:
        raise ValueError(
            "类型必须是income或expense"
        )


    return transaction_type