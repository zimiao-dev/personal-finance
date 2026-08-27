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
