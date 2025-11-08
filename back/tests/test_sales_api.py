import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
import types
import pytest

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from back.src.index import app


@pytest.fixture()
def client():
    app.config.update(TESTING=True)
    return app.test_client()


def test_sales_missing_dates_returns_400(client):
    """Should return 400 when start_date or end_date is missing"""
    resp = client.get("/api/sales-data")
    assert resp.status_code == 400
    data = resp.get_json()
    assert "error" in data
    assert "start_date and end_date" in data["error"]


def test_sales_valid_dates_returns_summary(client, monkeypatch):
    """Should return mocked summary when valid dates are given"""
    from back.src.routes import sales

    def fake_fetch_sales_data(start, end):
        assert isinstance(start, datetime)
        assert isinstance(end, datetime)
        return {"revenue": 1000, "sales": 20, "transactions": 10}

    monkeypatch.setattr(sales, "fetch_sales_data", fake_fetch_sales_data)

    resp = client.get("/api/sales-data?start_date=2024-01-01&end_date=2024-01-02")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data == {"revenue": 1000, "sales": 20, "transactions": 10}


def test_sales_daily_data(client, monkeypatch):
    """Should query a single day when start_date equals end_date"""
    from back.src.routes import sales
    captured = {}

    def fake_fetch_sales_data(start, end):
        captured["start"] = start
        captured["end"] = end
        return {"revenue": 500, "sales": 5, "transactions": 2}

    monkeypatch.setattr(sales, "fetch_sales_data", fake_fetch_sales_data)

    resp = client.get("/api/sales-data?start_date=2024-01-01&end_date=2024-01-01")
    assert resp.status_code == 200
    assert captured["start"] == datetime(2024, 1, 1, 0, 0, 0)
    assert captured["end"] == datetime(2024, 1, 1, 23, 59, 59)
    assert resp.json["revenue"] == 500
    assert resp.json["sales"] == 5
    assert resp.json["transactions"] == 2

def test_sales_exception_rolls_back_and_returns_500(client, monkeypatch):
    """Should rollback DB and return error JSON when exception occurs"""
    from back.src.routes import sales

    def fake_fetch_sales_data(start, end):
        raise Exception("DB error")

    fake_db = types.SimpleNamespace(session=types.SimpleNamespace(rollback=lambda: setattr(fake_db, "rolled", True)))
    monkeypatch.setattr(sales, "fetch_sales_data", fake_fetch_sales_data)
    monkeypatch.setattr(sales, "db", fake_db)

    resp = client.get("/api/sales-data?start_date=2024-01-01&end_date=2024-01-02")
    assert resp.status_code == 500

    data = resp.get_json()
    assert data["error"] == "DB error"
    assert getattr(fake_db, "rolled", False)
