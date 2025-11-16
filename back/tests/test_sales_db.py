import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime

@patch("src.database.sales.db")
def test_fetch_sales_data_returns_correct_values(mock_db):
    """fetch_sales_data should return correct numbers from query result."""
    from src.database.sales import fetch_sales_data

    # Mock the query result
    mock_result = {"revenue": 200.75, "sales": 15, "transactions": 3}
    mock_db.session.execute.return_value.mappings.return_value.first.return_value = mock_result

    start = datetime(2024, 1, 1)
    end = datetime(2024, 1, 2)

    summary = fetch_sales_data(start, end)
    assert summary == mock_result


@patch("src.database.sales.db")
def test_fetch_sales_data_handles_missing_values(mock_db):
    """Should safely handle None values and replace with 0."""
    from src.database.sales import fetch_sales_data

    mock_result = {"revenue": None, "sales": None, "transactions": None}
    mock_db.session.execute.return_value.mappings.return_value.first.return_value = mock_result

    start = datetime(2024, 1, 1)
    end = datetime(2024, 1, 2)

    summary = fetch_sales_data(start, end)
    assert summary == {"revenue": 0.0, "sales": 0, "transactions": 0}


@patch("src.database.sales.db")
def test_fetch_sales_data_raises_and_rolls_back(mock_db):
    """If query fails, function should rollback and raise error."""
    from src.database.sales import fetch_sales_data

    mock_db.session.execute.side_effect = Exception("SQL failed")

    with pytest.raises(Exception):
        fetch_sales_data(datetime(2024, 1, 1), datetime(2024, 1, 2))

    mock_db.session.rollback.assert_called_once()
