from datetime import datetime


def validate_amount(amount: str) -> float:
    """
    校验金额
    """

    try:
        amount = float(amount.strip())

    except (ValueError, TypeError, AttributeError):
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

    date_str = date_str.strip()

    try:
        datetime.strptime(
            date_str,
            "%Y-%m-%d"
        )

    except (ValueError, AttributeError):
        raise ValueError(
            "日期格式错误，应为 YYYY-MM-DD"
        )


    return date_str



def validate_type(transaction_type: str) -> str:
    """
    校验交易类型
    """

    transaction_type = (
        transaction_type
        .strip()
        .lower()
    )


    if transaction_type not in [
        "income",
        "expense"
    ]:
        raise ValueError(
            "类型必须是income或expense"
        )


    return transaction_type



def validate_id(id_str: str) -> int:
    """
    校验ID
    """

    try:
        transaction_id = int(id_str)

    except (ValueError, TypeError):
        raise ValueError(
            "ID必须为整数"
        )

    if transaction_id <= 0:
        raise ValueError(
            "ID必须大于0"
        )

    return transaction_id



def validate_category(category: str) -> str:
    """
    校验分类
    """

    category = category.strip()

    if not category:
        raise ValueError(
            "分类不能为空"
        )

    return category



def validate_date_range(
    start_date,
    end_date
) -> None:
    """
    日期范围校验
    """

    if start_date > end_date:
        raise ValueError(
            "开始日期不能晚于结束日期"
        )