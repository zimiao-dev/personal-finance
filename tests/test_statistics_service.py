import pytest

from models import TransactionStatistics
from services import statistics_service


def test_get_transaction_statistics_maps_repository_data_to_model(
    monkeypatch,
):
    repository_data = {
        "total_income": 100.0,
        "total_expense": 40.0,
        "transaction_count": 3,
    }

    def fake_get_statistics(start_date, end_date):
        return repository_data

    monkeypatch.setattr(
        statistics_service,
        "get_statistics",
        fake_get_statistics,
    )

    result = statistics_service.get_transaction_statistics()

    assert isinstance(result, TransactionStatistics)
    assert result.total_income == repository_data["total_income"]
    assert result.total_expense == repository_data["total_expense"]
    assert result.transaction_count == repository_data["transaction_count"]
    assert result.balance == (
        repository_data["total_income"]
        - repository_data["total_expense"]
    )


def test_get_transaction_statistics_passes_date_range_to_repository(
    monkeypatch,
):
    start_date = "2026-08-01"
    end_date = "2026-08-24"
    calls = []

    repository_data = {
        "total_income": 100.0,
        "total_expense": 40.0,
        "transaction_count": 3,
    }

    def fake_get_statistics(received_start_date, received_end_date):
        calls.append(
            (received_start_date, received_end_date)
        )
        return repository_data

    monkeypatch.setattr(
        statistics_service,
        "get_statistics",
        fake_get_statistics,
    )

    statistics_service.get_transaction_statistics(
        start_date,
        end_date,
    )

    assert calls == [
        (start_date, end_date)
    ]


def test_get_transaction_statistics_passes_none_dates_by_default(
    monkeypatch,
):
    calls = []

    repository_data = {
        "total_income": 100.0,
        "total_expense": 40.0,
        "transaction_count": 3,
    }

    def fake_get_statistics(received_start_date, received_end_date):
        calls.append(
            (received_start_date, received_end_date)
        )
        return repository_data

    monkeypatch.setattr(
        statistics_service,
        "get_statistics",
        fake_get_statistics,
    )

    statistics_service.get_transaction_statistics()

    assert calls == [
        (None, None)
    ]


def test_get_transaction_statistics_propagates_repository_value_error(
    monkeypatch,
):
    error_message = "repository test failure"

    def fake_get_statistics(start_date, end_date):
        raise ValueError(error_message)

    monkeypatch.setattr(
        statistics_service,
        "get_statistics",
        fake_get_statistics,
    )

    with pytest.raises(
        ValueError,
        match=error_message,
    ):
        statistics_service.get_transaction_statistics()
