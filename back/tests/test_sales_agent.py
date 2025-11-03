import sys
import os
import pytest
import base64
import pandas as pd
from unittest.mock import MagicMock

mock_supervisor = MagicMock()
sys.modules["langgraph_supervisor"] = mock_supervisor
sys.modules["langgraph_supervisor.supervisor"] = MagicMock()
sys.modules["langgraph_supervisor.handoff"] = MagicMock()

mock_prebuilt = MagicMock()
mock_prebuilt.create_react_agent = MagicMock(return_value=MagicMock())
sys.modules["langgraph.prebuilt"] = mock_prebuilt

from ..src.services.sales_agent import SalesTool, SalesAgent


@pytest.fixture
def mock_sales_data():
    """Provide fake sales data for mocking database results"""
    data = {
        "date": pd.date_range("2025-09-01", periods=5, freq="D"),
        "product": ["A", "B", "C", "A", "B"],
        "items_sold": [100, 200, 300, 400, 500],
        "revenue": [1000.0, 2000.0, 3000.0, 4000.0, 5000.0],
    }
    df = pd.DataFrame(data)
    df["month"] = df["date"].dt.to_period("M")
    return df

@pytest.fixture
def sales_tool(mock_sales_data):
    """Patch _fetch_sales_data to return mock dataframe"""
    tool = SalesTool()
    tool._fetch_sales_data = MagicMock(return_value=mock_sales_data)
    return tool

@pytest.fixture(autouse=True)
def patch_sales_tool_fetch(monkeypatch):
    """Automatically mock database calls for all SalesTool instances."""
    mock_df = pd.DataFrame({
        "date": pd.date_range("2025-09-01", periods=5, freq="D"),
        "product": ["A", "B", "C", "A", "B"],
        "items_sold": [10, 20, 30, 40, 50],
        "revenue": [100.0, 200.0, 300.0, 400.0, 500.0],
    })
    mock_df["month"] = mock_df["date"].dt.to_period("M")

    from ..src.services import sales_agent as module
    monkeypatch.setattr(module.sales_tool, "_fetch_sales_data", lambda *a, **kw: mock_df)
    monkeypatch.setattr(module.sales_agent_instance.tool, "_fetch_sales_data", lambda *a, **kw: mock_df)

def test_generate_sales_report(sales_tool):
    agent = SalesAgent(sales_tool)
    request = {"task": "sales_report", "group_by": "month"}
    report = agent.handle_request(request)

    assert isinstance(report, dict)
    assert report["status"] == "success"
    assert "data" in report
    data = report["data"]

    assert isinstance(data, list)
    assert len(data) == 1
    month_data = data[0]
    expected_keys = {
        "period",
        "total_revenue",
        "total_items_sold",
        "best_selling_product",
        "best_selling_product_units",
    }
    assert set(month_data.keys()) == expected_keys
    assert month_data["period"] == "2025-09"
    assert isinstance(month_data["total_revenue"], float)
    assert isinstance(month_data["total_items_sold"], int)
    assert isinstance(month_data["best_selling_product"], str)
    assert isinstance(month_data["best_selling_product_units"], int)

def test_create_sales_graph_success(sales_tool):
    agent = SalesAgent(sales_tool)
    month = "2025-09"

    result = agent.handle_request({"task": "create_graph", "month": month})

    assert isinstance(result, dict)
    assert result["type"] == "image"
    assert "data" in result

    try:
        image_bytes = base64.b64decode(result["data"])
        assert len(image_bytes) > 0
    except Exception as e: # pragma: no cover
        pytest.fail(f"Failed to decode base64 image data: {e}") # pragma: no cover

def test_create_sales_graph_invalid_month():
    tool = SalesTool()
    tool._fetch_sales_data = MagicMock(return_value=pd.DataFrame())
    agent = SalesAgent(tool)

    result = agent.handle_request({"task": "create_graph", "month": "3000-01"})

    assert isinstance(result, dict)
    assert result["status"] == "error"
    assert "No sales data" in result["message"]

def test_create_sales_graph_missing_month():
    agent = SalesAgent(sales_tool)

    with pytest.raises(ValueError, match="Month parameter is required"):
        agent.handle_request({"task": "create_graph"})

def test_unknown_task(sales_tool):
    agent = SalesAgent(sales_tool)
    result = agent.handle_request({"task": "unknown_task"})

    assert "Unknown task" in result

def test_create_sales_graph_bar_chart(sales_tool):
    agent = SalesAgent(sales_tool)
    month = "2025-09"

    result = sales_tool.create_sales_graph(month, graph_type="bar")

    assert isinstance(result, dict)
    assert result["type"] == "image"
    assert "data" in result

    try:
        image_bytes = base64.b64decode(result["data"])
        assert len(image_bytes) > 0
    except Exception as e: # pragma: no cover
        pytest.fail(f"Failed to decode base64 image data: {e}") # pragma: no cover

def test_sales_tool_generate_report_calculations(sales_tool):
    """Test that generate_sales_report calculates correct aggregations"""
    report = sales_tool.generate_sales_report()
    assert report["status"] == "success"

    data = report["data"]
    for period_data in data:
        assert "period" in period_data
        assert "total_revenue" in period_data
        assert "total_items_sold" in period_data
        assert "best_selling_product" in period_data
        assert "best_selling_product_units" in period_data

        assert isinstance(period_data["total_revenue"], float)
        assert isinstance(period_data["total_items_sold"], int)
        assert isinstance(period_data["best_selling_product"], str)
        assert isinstance(period_data["best_selling_product_units"], int)

        assert period_data["total_revenue"] >= 0
        assert period_data["total_items_sold"] >= 0
        assert period_data["best_selling_product_units"] >= 0

def test_tool_wrapper_generate_sales_report():
    from ..src.services.sales_agent import generate_sales_report as tool_func

    result = tool_func.invoke({})

    assert isinstance(result, dict)
    assert "status" in result
    assert "data" in result

def test_tool_wrapper_create_sales_graph():
    from ..src.services.sales_agent import create_sales_graph as tool_func

    result = tool_func.invoke({"month": "2025-09"})

    assert isinstance(result, dict)
    assert result["type"] == "image"
    assert "data" in result

def test_sales_agent_initialization():
    from ..src.services.sales_agent import sales_agent
    assert sales_agent is not None
