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


@dataclass
class TransactionStatistics:
    """
    用户收支统计结果
    """

    total_income: float

    total_expense: float

    @property
    def balance(self) -> float:
        """
        收支差额
        """
        return self.total_income - self.total_expense