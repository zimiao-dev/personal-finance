from dataclasses import dataclass


@dataclass
class Transaction:
    """
    用户交易记录模型
    """

    id: int | None

    amount: float

    type: str

    category: str

    transaction_date: str

    description: str | None = None
