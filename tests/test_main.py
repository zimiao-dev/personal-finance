from models import Transaction, TransactionStatistics
import main


def test_add_bill_validates_inputs_and_passes_transaction_to_service(
    monkeypatch,
):
    raw_amount = " 15.0 "
    raw_type = "income "
    raw_category = " food"
    raw_date = "2026-08-25 "
    raw_description = "午餐"

    input_values = iter([
        raw_amount,
        raw_type,
        raw_category,
        raw_date,
        raw_description,
    ])

    def fake_input(prompt=""):
        return next(input_values)

    monkeypatch.setattr(
        "builtins.input",
        fake_input,
    )

    validated_amount = 15.0
    validated_type = "income"
    validated_category = "food"
    validated_date = "2026-08-25"

    validator_calls = []

    def fake_validate_amount(received_value):
        validator_calls.append(("amount", received_value))
        return validated_amount

    def fake_validate_type(received_value):
        validator_calls.append(("type", received_value))
        return validated_type

    def fake_validate_category(received_value):
        validator_calls.append(("category", received_value))
        return validated_category

    def fake_validate_date(received_value):
        validator_calls.append(("date", received_value))
        return validated_date

    monkeypatch.setattr(
        main,
        "validate_amount",
        fake_validate_amount,
    )
    monkeypatch.setattr(
        main,
        "validate_type",
        fake_validate_type,
    )
    monkeypatch.setattr(
        main,
        "validate_category",
        fake_validate_category,
    )
    monkeypatch.setattr(
        main,
        "validate_date",
        fake_validate_date,
    )

    inserted_id = 515
    service_calls = []

    def fake_add_transaction(received_transaction):
        service_calls.append(received_transaction)
        return inserted_id

    monkeypatch.setattr(
        main,
        "add_transaction",
        fake_add_transaction,
    )

    result = main.add_bill()

    assert validator_calls == [
        ("amount", raw_amount),
        ("type", raw_type),
        ("category", raw_category),
        ("date", raw_date),
    ]

    assert len(service_calls) == 1

    created_transaction = service_calls[0]

    assert isinstance(created_transaction, Transaction)
    assert created_transaction.id is None
    assert created_transaction.amount == validated_amount
    assert created_transaction.type == validated_type
    assert created_transaction.category == validated_category
    assert created_transaction.transaction_date == validated_date
    assert created_transaction.description == raw_description

    assert result == inserted_id


def test_list_bill_displays_empty_message_when_no_transactions_exist(
    monkeypatch,
    capsys,
):
    calls = []

    def fake_get_all_transactions():
        calls.append(True)
        return []

    monkeypatch.setattr(
        main,
        "get_all_transactions",
        fake_get_all_transactions,
    )

    main.list_bill()

    captured = capsys.readouterr()

    assert calls == [True]

    assert "暂无账单记录" in captured.out


def test_update_bill_displays_not_found_message_for_missing_transaction(
    monkeypatch,
    capsys,
):
    raw_id = "515 "
    validated_id = 515

    input_values = iter([
        raw_id,
    ])

    def fake_input(prompt=""):
        return next(input_values)

    monkeypatch.setattr(
        "builtins.input",
        fake_input,
    )

    validator_calls = []

    def fake_validate_id(received_id):
        validator_calls.append(received_id)
        return validated_id

    monkeypatch.setattr(
        main,
        "validate_id",
        fake_validate_id,
    )

    query_calls = []

    def fake_get_transaction_by_id(received_id):
        query_calls.append(received_id)
        return None

    monkeypatch.setattr(
        main,
        "get_transaction_by_id",
        fake_get_transaction_by_id,
    )

    update_calls = []

    def fake_update_transaction(received_transaction):
        update_calls.append(received_transaction)
        return None

    monkeypatch.setattr(
        main,
        "update_transaction",
        fake_update_transaction,
    )

    main.update_bill()

    captured = capsys.readouterr()

    assert validator_calls == [raw_id]

    assert query_calls == [validated_id]

    assert update_calls == []

    assert "账单记录不存在！" in captured.out


def test_statistics_bill_displays_empty_message_when_count_is_zero(
    monkeypatch,
    capsys,
):
    input_values = iter([
        "a",
    ])

    def fake_input(prompt=""):
        return next(input_values)

    monkeypatch.setattr(
        "builtins.input",
        fake_input,
    )

    service_calls = []

    statistics_result = TransactionStatistics(
        total_income=0,
        total_expense=0,
        transaction_count=0,
    )

    def fake_get_transaction_statistics(
        received_start_date,
        received_end_date,
    ):
        service_calls.append(
            (received_start_date, received_end_date)
        )
        return statistics_result

    monkeypatch.setattr(
        main,
        "get_transaction_statistics",
        fake_get_transaction_statistics,
    )

    main.statistics_bill()

    captured = capsys.readouterr()

    assert service_calls == [
        (None, None),
    ]

    assert "暂无统计数据" in captured.out

    assert "统计结果：" not in captured.out


def test_query_bill_displays_empty_message_when_no_transactions_match(
    monkeypatch,
    capsys,
):
    # Arrange
    query_mode = "a"
    raw_category = "  food  "
    validated_category = "food"

    input_values = iter([
        query_mode,
        raw_category,
    ])

    def fake_input(prompt=""):
        return next(input_values)

    monkeypatch.setattr(
        "builtins.input",
        fake_input,
    )

    validator_calls = []

    def fake_validate_category(received_category):
        validator_calls.append(received_category)
        return validated_category

    monkeypatch.setattr(
        main,
        "validate_category",
        fake_validate_category,
    )

    service_calls = []

    def fake_query_transactions(
        *,
        category,
        start_date,
        end_date,
    ):
        service_calls.append(
            {
                "category": category,
                "start_date": start_date,
                "end_date": end_date,
            }
        )
        return []

    monkeypatch.setattr(
        main,
        "query_transactions",
        fake_query_transactions,
    )

    # Act
    main.query_bill()

    captured = capsys.readouterr()

    # Assert
    assert validator_calls == [
        raw_category,
    ]

    assert service_calls == [
        {
            "category": validated_category,
            "start_date": None,
            "end_date": None,
        }
    ]

    assert "没有符合条件的账单记录！" in captured.out
    assert "查询结果如下：" not in captured.out


def test_delete_bill_displays_not_found_message_for_missing_transaction(
    monkeypatch,
    capsys,
):
    # Arrange
    raw_id = " 515 "
    validated_id = 515

    input_values = iter(
        [
            raw_id,
        ]
    )

    def fake_input(prompt=""):
        return next(input_values)

    monkeypatch.setattr(
        "builtins.input",
        fake_input,
    )

    validator_calls = []

    def fake_validate_id(received_id):
        validator_calls.append(received_id)
        return validated_id

    monkeypatch.setattr(
        main,
        "validate_id",
        fake_validate_id,
    )

    query_calls = []

    def fake_get_transaction_by_id(received_id):
        query_calls.append(received_id)
        return None

    monkeypatch.setattr(
        main,
        "get_transaction_by_id",
        fake_get_transaction_by_id,
    )

    delete_calls = []

    def fake_delete_transaction(received_id):
        delete_calls.append(received_id)
        return 0

    monkeypatch.setattr(
        main,
        "delete_transaction",
        fake_delete_transaction,
    )

    # Act
    main.delete_bill()

    captured = capsys.readouterr()

    # Assert
    assert validator_calls == [
        raw_id,
    ]

    assert query_calls == [
        validated_id,
    ]

    assert delete_calls == []

    assert "账单不存在！" in captured.out


def test_update_bill_cancels_when_not_confirmed(
    monkeypatch,
    capsys,
):
    # Arrange
    raw_id = " 515 "
    validated_id = 515
    cancel_choice = " N"

    existing_transaction = Transaction(
        id=validated_id,
        amount=12.0,
        type="expense",
        category="food",
        transaction_date="2026-08-27",
        description="早餐",
    )

    input_values = iter(
        [
            raw_id,
            cancel_choice,
        ]
    )

    def fake_input(prompt=""):
        return next(input_values)

    monkeypatch.setattr(
        "builtins.input",
        fake_input,
    )

    validator_calls = []

    def fake_validate_id(received_id):
        validator_calls.append(received_id)
        return validated_id

    monkeypatch.setattr(
        main,
        "validate_id",
        fake_validate_id,
    )

    query_calls = []

    def fake_get_transaction_by_id(received_id):
        query_calls.append(received_id)
        return existing_transaction

    monkeypatch.setattr(
        main,
        "get_transaction_by_id",
        fake_get_transaction_by_id,
    )

    update_calls = []

    def fake_update_transaction(received_transaction):
        update_calls.append(received_transaction)
        return 1

    monkeypatch.setattr(
        main,
        "update_transaction",
        fake_update_transaction,
    )

    # Act
    main.update_bill()

    captured = capsys.readouterr()

    # Assert
    assert validator_calls == [
        raw_id,
    ]

    assert query_calls == [
        validated_id,
    ]

    assert update_calls == []

    assert "当前账单:" in captured.out
    assert "取消修改" in captured.out


def test_list_bill_displays_returned_transactions(
    monkeypatch,
    capsys,
):
    # Arrange
    first_transaction = Transaction(
        id=315,
        amount=12.0,
        type="expense",
        category="food",
        transaction_date="2026-08-26",
        description="午餐",
    )

    second_transaction = Transaction(
        id=515,
        amount=4.0,
        type="income",
        category="transport",
        transaction_date="2026-08-27",
        description="交通补贴",
    )

    returned_transactions = [
        first_transaction,
        second_transaction,
    ]

    service_calls = []

    def fake_get_all_transactions():
        service_calls.append(True)
        return returned_transactions

    monkeypatch.setattr(
        main,
        "get_all_transactions",
        fake_get_all_transactions,
    )

    # Act
    main.list_bill()

    captured = capsys.readouterr()

    # Assert
    assert service_calls == [True]

    assert "全部历史账单如下：" in captured.out
    assert str(first_transaction) in captured.out
    assert str(second_transaction) in captured.out
    assert "暂无账单记录" not in captured.out


def test_statistics_bill_displays_statistics_when_transactions_exist(
    monkeypatch,
    capsys,
):
    # Arrange
    statistics_mode = "  A"

    input_values = iter([
        statistics_mode,
    ])

    def fake_input(prompt=""):
        return next(input_values)

    monkeypatch.setattr(
        "builtins.input",
        fake_input,
    )

    statistics_result = TransactionStatistics(
        total_income=515.15,
        total_expense=15.0,
        transaction_count=20,
    )

    service_calls = []

    def fake_get_transaction_statistics(
        received_start_date,
        received_end_date,
    ):
        service_calls.append(
            (received_start_date, received_end_date)
        )
        return statistics_result

    monkeypatch.setattr(
        main,
        "get_transaction_statistics",
        fake_get_transaction_statistics,
    )

    # Act
    main.statistics_bill()

    captured = capsys.readouterr()

    # Assert
    assert (
        f"总收入：{statistics_result.total_income}"
        in captured.out
    )

    assert (
        f"总支出：{statistics_result.total_expense}"
        in captured.out
    )

    assert (
        f"收支差额：{statistics_result.balance}"
        in captured.out
    )

    assert "统计结果：" in captured.out
    assert "暂无统计数据" not in captured.out


def test_delete_bill_cancels_when_not_confirmed(
    monkeypatch,
    capsys,
):
    # Arrange
    raw_id = "  515"
    validated_id = 515
    cancel_choice = " N "

    existing_transaction = Transaction(
        id=validated_id,
        amount=15.0,
        type="expense",
        category="food",
        transaction_date="2026-08-27",
        description="早餐",
    )

    input_values = iter([
        raw_id,
        cancel_choice,
    ])

    def fake_input(prompt=""):
        return next(input_values)

    monkeypatch.setattr(
        "builtins.input",
        fake_input,
    )

    validator_calls = []

    def fake_validate_id(received_id):
        validator_calls.append(received_id)
        return validated_id

    monkeypatch.setattr(
        main,
        "validate_id",
        fake_validate_id,
    )

    query_calls = []

    def fake_get_transaction_by_id(received_id):
        query_calls.append(received_id)
        return existing_transaction

    monkeypatch.setattr(
        main,
        "get_transaction_by_id",
        fake_get_transaction_by_id,
    )

    delete_calls = []

    def fake_delete_transaction(received_id):
        delete_calls.append(received_id)
        return 1

    monkeypatch.setattr(
        main,
        "delete_transaction",
        fake_delete_transaction,
    )

    # Act
    main.delete_bill()

    captured = capsys.readouterr()

    # Assert
    assert validator_calls == [
        raw_id,
    ]

    assert query_calls == [
        validated_id,
    ]

    assert delete_calls == []

    assert "当前账单:" in captured.out
    assert "取消删除" in captured.out


def test_query_bill_passes_validated_date_range_to_service(
    monkeypatch,
):
    # Arrange
    query_mode = " B"
    raw_start_date = "  2026-08-01"
    raw_end_date = "2026-08-27  "

    validated_start_date = "2026-08-01"
    validated_end_date = "2026-08-27"

    input_values = iter(
        [
            query_mode,
            raw_start_date,
            raw_end_date,
        ]
    )

    def fake_input(prompt=""):
        return next(input_values)

    monkeypatch.setattr(
        "builtins.input",
        fake_input,
    )

    validated_date_values = iter(
        [
            validated_start_date,
            validated_end_date,
        ]
    )

    date_validator_calls = []

    def fake_validate_date(received_date):
        date_validator_calls.append(received_date)
        return next(validated_date_values)

    monkeypatch.setattr(
        main,
        "validate_date",
        fake_validate_date,
    )

    date_range_calls = []

    call_order = []

    def fake_validate_date_range(
        received_start_date,
        received_end_date,
    ):
        date_range_calls.append(
            (received_start_date, received_end_date)
        )

        call_order.append("validate_date_range")

        return None

    monkeypatch.setattr(
        main,
        "validate_date_range",
        fake_validate_date_range,
    )

    service_calls = []

    def fake_query_transactions(
        *,
        category,
        start_date,
        end_date,
    ):
        service_calls.append({
            "category": category,
            "start_date": start_date,
            "end_date": end_date,
        })

        call_order.append("query_transactions")

        return []

    monkeypatch.setattr(
        main,
        "query_transactions",
        fake_query_transactions,
    )

    # Act
    main.query_bill()

    # Assert
    assert date_validator_calls == [
        raw_start_date,
        raw_end_date,
    ]

    assert date_range_calls == [
        (validated_start_date, validated_end_date),
    ]

    assert service_calls == [
        {
            "category": None,
            "start_date": validated_start_date,
            "end_date": validated_end_date,
        }
    ]

    assert call_order == [
        "validate_date_range",
        "query_transactions",
    ]


def test_query_bill_passes_category_and_date_range_to_service(
    monkeypatch,
):
    # Arrange
    query_mode = "  C  "

    raw_category = "  food  "
    raw_start_date = "  2026-08-01"
    raw_end_date = "2026-08-27 "

    validated_category = "food"
    validated_start_date = "2026-08-01"
    validated_end_date = "2026-08-27"

    input_values = iter(
        [
            query_mode,
            raw_category,
            raw_start_date,
            raw_end_date,
        ]
    )

    def fake_input(prompt=""):
        return next(input_values)

    monkeypatch.setattr(
        "builtins.input",
        fake_input,
    )

    category_validator_calls = []

    def fake_validate_category(received_category):
        category_validator_calls.append(received_category)
        return validated_category

    monkeypatch.setattr(
        main,
        "validate_category",
        fake_validate_category,
    )

    validated_date_values = iter([
        validated_start_date,
        validated_end_date,
    ])

    date_validator_calls = []

    def fake_validate_date(received_date):
        date_validator_calls.append(received_date)
        return next(validated_date_values)

    monkeypatch.setattr(
        main,
        "validate_date",
        fake_validate_date,
    )

    date_range_calls = []

    call_order = []

    def fake_validate_date_range(
        received_start_date,
        received_end_date,
    ):
        date_range_calls.append(
            (received_start_date, received_end_date)
        )

        call_order.append("validate_date_range")

        return None

    monkeypatch.setattr(
        main,
        "validate_date_range",
        fake_validate_date_range,
    )

    service_calls = []

    def fake_query_transactions(
        *,
        category,
        start_date,
        end_date,
    ):
        service_calls.append({
            "category": category,
            "start_date": start_date,
            "end_date": end_date,
        })

        call_order.append("query_transactions")

        return []

    monkeypatch.setattr(
        main,
        "query_transactions",
        fake_query_transactions,
    )

    # Act
    main.query_bill()

    # Assert
    assert category_validator_calls == [
        raw_category,
    ]

    assert date_validator_calls == [
        raw_start_date,
        raw_end_date,
    ]

    assert date_range_calls == [
        (validated_start_date, validated_end_date),
    ]

    assert service_calls == [
        {
            "category": validated_category,
            "start_date": validated_start_date,
            "end_date": validated_end_date,
        }
    ]

    assert call_order == [
        "validate_date_range",
        "query_transactions",
    ]


def test_delete_bill_displays_success_after_confirmed_delete(
    monkeypatch,
    capsys,
):
    # Arrange
    raw_id = "  515 "
    validated_id = 515
    confirm_choice = " Y"

    existing_transaction = Transaction(
        id=validated_id,
        amount=15.0,
        type="expense",
        category="food",
        transaction_date="2026-08-27",
        description="午餐",
    )

    input_values = iter(
        [
            raw_id,
            confirm_choice,
        ]
    )

    def fake_input(prompt=""):
        return next(input_values)

    monkeypatch.setattr(
        "builtins.input",
        fake_input,
    )

    validator_calls = []

    def fake_validate_id(received_id):
        validator_calls.append(received_id)
        return validated_id

    monkeypatch.setattr(
        main,
        "validate_id",
        fake_validate_id,
    )

    query_calls = []

    def fake_get_transaction_by_id(received_id):
        query_calls.append(received_id)
        return existing_transaction

    monkeypatch.setattr(
        main,
        "get_transaction_by_id",
        fake_get_transaction_by_id,
    )

    delete_calls = []

    def fake_delete_transaction(received_id):
        delete_calls.append(received_id)

        return 1

    monkeypatch.setattr(
        main,
        "delete_transaction",
        fake_delete_transaction,
    )

    # Act
    main.delete_bill()

    captured = capsys.readouterr()

    # Assert
    assert validator_calls == [
        raw_id,
    ]

    assert query_calls == [
        validated_id,
    ]

    assert delete_calls == [
        validated_id,
    ]

    assert "当前账单:" in captured.out

    assert str(existing_transaction) in captured.out

    assert "删除成功！" in captured.out
    assert "取消删除" not in captured.out


def test_statistics_bill_passes_validated_date_range_to_service(
    monkeypatch,
):
    # Arrange
    statistics_mode = "  B "
    raw_start_date = "  2026-08-01"
    raw_end_date = "2026-08-27  "

    validated_start_date = "2026-08-01"
    validated_end_date = "2026-08-27"

    validated_date_values = iter(
        [
            validated_start_date,
            validated_end_date,
        ]
    )

    input_values = iter(
        [
            statistics_mode,
            raw_start_date,
            raw_end_date,
        ]
    )

    def fake_input(prompt=""):
        return next(input_values)

    monkeypatch.setattr(
        "builtins.input",
        fake_input,
    )

    date_validator_calls = []

    def fake_validate_date(received_date):
        date_validator_calls.append(received_date)
        return next(validated_date_values)

    monkeypatch.setattr(
        main,
        "validate_date",
        fake_validate_date,
    )

    date_range_calls = []

    call_order = []

    def fake_validate_date_range(
        received_start_date,
        received_end_date,
    ):
        date_range_calls.append(
            (
                received_start_date,
                received_end_date,
            )
        )

        call_order.append("validate_date_range")

        return None

    monkeypatch.setattr(
        main,
        "validate_date_range",
        fake_validate_date_range,
    )

    service_calls = []

    statistics_result = TransactionStatistics(
        total_income=515.15,
        total_expense=15.0,
        transaction_count=15,
    )

    def fake_get_transaction_statistics(
        received_start_date,
        received_end_date,
    ):
        service_calls.append(
            (received_start_date, received_end_date)
        )
        call_order.append("get_transaction_statistics")
        return statistics_result

    monkeypatch.setattr(
        main,
        "get_transaction_statistics",
        fake_get_transaction_statistics,
    )

    # Act
    main.statistics_bill()

    # Assert
    assert date_validator_calls == [
        raw_start_date,
        raw_end_date,
    ]

    assert date_range_calls == [
        (
            validated_start_date,
            validated_end_date,
        ),
    ]

    assert service_calls == [
        (
            validated_start_date,
            validated_end_date,
        ),
    ]

    assert call_order == [
        "validate_date_range",
        "get_transaction_statistics",
    ]


def test_update_bill_displays_success_after_confirmed_update(
    monkeypatch,
    capsys,
):
    # Arrange
    raw_id = "  515 "
    validated_id = 515
    confirm_choice = "  Y "

    raw_amount = "15.0 "
    raw_type = "  Expense"
    raw_category = "food "
    raw_date = "2026-08-26 "
    raw_description = " 晚餐"

    validated_amount = 15.0
    validated_type = "expense"
    validated_category = "food"
    validated_date = "2026-08-26"

    existing_transaction = Transaction(
        id=validated_id,
        amount=10.0,
        type="income",
        category="transport",
        transaction_date="2026-08-28",
        description="地铁",
    )

    input_values = iter([
        raw_id,
        confirm_choice,
        raw_amount,
        raw_type,
        raw_category,
        raw_date,
        raw_description,
    ])

    def fake_input(prompt=""):
        return next(input_values)

    monkeypatch.setattr(
        "builtins.input",
        fake_input,
    )

    validator_calls = []

    def fake_validate_id(received_value):
        validator_calls.append(("id", received_value))
        return validated_id

    def fake_validate_amount(received_value):
        validator_calls.append(("amount", received_value))
        return validated_amount

    def fake_validate_type(received_value):
        validator_calls.append(("type", received_value))
        return validated_type

    def fake_validate_category(received_value):
        validator_calls.append(("category", received_value))
        return validated_category

    def fake_validate_date(received_value):
        validator_calls.append(("date", received_value))
        return validated_date

    monkeypatch.setattr(
        main,
        "validate_id",
        fake_validate_id,
    )
    monkeypatch.setattr(
        main,
        "validate_amount",
        fake_validate_amount,
    )
    monkeypatch.setattr(
        main,
        "validate_type",
        fake_validate_type,
    )
    monkeypatch.setattr(
        main,
        "validate_category",
        fake_validate_category,
    )
    monkeypatch.setattr(
        main,
        "validate_date",
        fake_validate_date,
    )

    query_calls = []

    def fake_get_transaction_by_id(received_id):
        query_calls.append(received_id)
        return existing_transaction

    monkeypatch.setattr(
        main,
        "get_transaction_by_id",
        fake_get_transaction_by_id,
    )

    update_calls = []

    def fake_update_transaction(received_transaction):
        update_calls.append(received_transaction)

        return 1

    monkeypatch.setattr(
        main,
        "update_transaction",
        fake_update_transaction,
    )

    # Act
    main.update_bill()

    captured = capsys.readouterr()

    # Assert
    assert validator_calls == [
        ("id", raw_id),
        ("amount", raw_amount),
        ("type", raw_type),
        ("category", raw_category),
        ("date", raw_date),
    ]

    assert query_calls == [
        validated_id,
    ]

    assert len(update_calls) == 1
    updated_transaction = update_calls[0]

    assert isinstance(updated_transaction, Transaction)
    assert updated_transaction.id == validated_id
    assert updated_transaction.amount == validated_amount
    assert updated_transaction.type == validated_type
    assert updated_transaction.category == validated_category
    assert updated_transaction.transaction_date == validated_date
    assert updated_transaction.description == raw_description

    assert updated_transaction is not existing_transaction

    assert "当前账单:" in captured.out
    assert str(existing_transaction) in captured.out
    assert "修改成功" in captured.out
    assert "取消修改" not in captured.out


def test_delete_bill_displays_failure_when_delete_affects_no_rows(
    monkeypatch,
    capsys,
):
    # Arrange
    raw_id = "515"
    validated_id = 515
    confirm_choice = "  Y "

    existing_transaction = Transaction(
        id=validated_id,
        amount=15.0,
        type="expense",
        category="food",
        transaction_date="2026-08-26",
        description="午餐",
    )

    input_values = iter([
        raw_id,
        confirm_choice,
    ])

    def fake_input(prompt=""):
        return next(input_values)

    monkeypatch.setattr(
        "builtins.input",
        fake_input,
    )

    validator_calls = []

    def fake_validate_id(received_id):
        validator_calls.append(received_id)
        return validated_id

    monkeypatch.setattr(
        main,
        "validate_id",
        fake_validate_id,
    )

    query_calls = []

    def fake_get_transaction_by_id(received_id):
        query_calls.append(received_id)
        return existing_transaction

    monkeypatch.setattr(
        main,
        "get_transaction_by_id",
        fake_get_transaction_by_id,
    )

    delete_calls = []

    def fake_delete_transaction(received_id):
        delete_calls.append(received_id)

        return 0

    monkeypatch.setattr(
        main,
        "delete_transaction",
        fake_delete_transaction,
    )

    # Act
    main.delete_bill()

    captured = capsys.readouterr()

    # Assert
    assert validator_calls == [
        raw_id,
    ]

    assert query_calls == [
        validated_id,
    ]

    assert delete_calls == [
        validated_id,
    ]

    assert "当前账单:" in captured.out
    assert str(existing_transaction) in captured.out

    assert "删除失败！" in captured.out
    assert "删除成功！" not in captured.out
    assert "取消删除" not in captured.out
