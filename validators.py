import math
import re
from datetime import datetime


DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def validate_amount(amount: str) -> float:
    """校验金额"""

    try:
        value = float(amount.strip())
    except (ValueError, TypeError, AttributeError):
        raise ValueError("金额必须为数字") from None

    if not math.isfinite(value):
        raise ValueError("金额必须是有限数字")

    if value <= 0:
        raise ValueError("金额必须大于0")

    return value


def validate_date(date_str: str) -> str:
    """校验日期格式"""

    try:
        date_str = date_str.strip()
    except AttributeError:
        raise ValueError("日期格式错误，应为 YYYY-MM-DD") from None

    if not DATE_PATTERN.fullmatch(date_str):
        raise ValueError("日期格式错误，应为 YYYY-MM-DD")

    try:
        datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        raise ValueError("日期格式错误，应为 YYYY-MM-DD") from None

    return date_str


def validate_type(transaction_type: str) -> str:
    """校验交易类型"""

    try:
        transaction_type = transaction_type.strip().lower()
    except AttributeError:
        raise ValueError("类型必须是income或expense") from None

    if transaction_type not in ("income", "expense"):
        raise ValueError("类型必须是income或expense")

    return transaction_type


def validate_id(id_str: str) -> int:
    """校验ID"""

    try:
        transaction_id = int(id_str)
    except (ValueError, TypeError):
        raise ValueError("ID必须为整数") from None

    if transaction_id <= 0:
        raise ValueError("ID必须大于0")

    return transaction_id


def validate_category(category: str) -> str:
    """校验分类"""

    try:
        category = category.strip()
    except AttributeError:
        raise ValueError("分类不能为空") from None

    if not category:
        raise ValueError("分类不能为空")

    return category


def validate_date_range(start_date: str, end_date: str) -> None:
    """校验日期范围"""

    if start_date > end_date:
        raise ValueError("开始日期不能晚于结束日期")
