import sys
import os
import pytest
import base64
from unittest.mock import MagicMock

mock_supervisor = MagicMock()
sys.modules["langgraph_supervisor"] = mock_supervisor
sys.modules["langgraph_supervisor.supervisor"] = MagicMock()
sys.modules["langgraph_supervisor.handoff"] = MagicMock()

mock_prebuilt = MagicMock()
mock_prebuilt.create_react_agent = MagicMock(return_value=MagicMock())
sys.modules["langgraph.prebuilt"] = mock_prebuilt

from ..src.services.sales_agent import SalesTool, SalesAgent


csv_path = os.path.join(os.path.dirname(__file__), "../src/data/mock_month_sales_data.csv")

@pytest.fixture
def sales_tool():
    tool_instance = SalesTool(csv_path)
    return tool_instance

def test_generate_sales_report(sales_tool):
    agent = SalesAgent(sales_tool)
    request = {"task": "sales_report"}
    report = agent.handle_request(request)

    assert isinstance(report, list)
    assert len(report) == 1
    month_data = report[0]
    expected_keys = {
        "month",
        "total_revenue",
        "total_items_sold",
        "best_selling_product",
        "best_selling_product_units",
    }
    assert set(month_data.keys()) == expected_keys
    assert month_data["month"] == "2025-09"
    assert month_data["total_revenue"] == 21790.40
    assert month_data["total_items_sold"] == 2558
    assert month_data["best_selling_product"] == "G"
    assert month_data["best_selling_product_units"] == 636

def test_create_sales_graph_success(sales_tool):
    agent = SalesAgent(sales_tool)
    month = "2025-09"

    result = agent.handle_request({"task": "create_graph", "month": month})

    assert isinstance(result, dict)
    assert result["type"] == "image"
    assert result["source_type"] == "base64"
    assert result["mime_type"] == "image/jpeg"
    assert "data" in result

    try:
        image_bytes = base64.b64decode(result["data"])
        assert len(image_bytes) > 0
    except Exception as e:
        pytest.fail(f"Failed to decode base64 image data: {e}")

def test_create_sales_graph_invalid_month(sales_tool):
    agent = SalesAgent(sales_tool)
    month = "3000-01"

    result = agent.handle_request({"task": "create_graph", "month": month})

    assert isinstance(result, dict)
    assert result["status"] == "error"
    assert "No sales data" in result["message"]

def test_create_sales_graph_missing_month():
    agent = SalesAgent(SalesTool(csv_path))

    with pytest.raises(ValueError, match="Month parameter is required"):
        agent.handle_request({"task": "create_graph"})

def test_unknown_task(sales_tool):
    agent = SalesAgent(sales_tool)
    result = agent.handle_request({"task": "unknown_task"})

    assert "Unknown task" in result

def test_sales_tool_init_file_not_found():
    with pytest.raises(FileNotFoundError, match="Sales data not found"):
        SalesTool("/non/existent/path.csv")

def test_sales_tool_init_invalid_csv(tmp_path):
    invalid_csv = tmp_path / "invalid.csv"
    invalid_csv.write_text("not,valid,csv\ndata")

    with pytest.raises(ValueError, match="Failed to read CSV"):
        SalesTool(str(invalid_csv))

def test_create_sales_graph_bar_chart(sales_tool):
    agent = SalesAgent(sales_tool)
    month = "2025-09"

    result = sales_tool.create_sales_graph(month, graph_type="bar")

    assert isinstance(result, dict)
    assert result["type"] == "image"
    assert result["source_type"] == "base64"
    assert result["mime_type"] == "image/jpeg"
    assert "data" in result

    try:
        image_bytes = base64.b64decode(result["data"])
        assert len(image_bytes) > 0
    except Exception as e:
        pytest.fail(f"Failed to decode base64 image data: {e}")

def test_sales_tool_generate_report_calculations(sales_tool):
    """Test that generate_sales_report calculates correct aggregations"""
    report = sales_tool.generate_sales_report()

    assert isinstance(report, list)
    for month_data in report:
        assert "month" in month_data
        assert "total_revenue" in month_data
        assert "total_items_sold" in month_data
        assert "best_selling_product" in month_data
        assert "best_selling_product_units" in month_data

        assert isinstance(month_data["total_revenue"], float)
        assert isinstance(month_data["total_items_sold"], int)
        assert isinstance(month_data["best_selling_product"], str)
        assert isinstance(month_data["best_selling_product_units"], int)

        assert month_data["total_revenue"] >= 0
        assert month_data["total_items_sold"] >= 0
        assert month_data["best_selling_product_units"] >= 0

def test_tool_wrapper_generate_sales_report():
    from ..src.services.sales_agent import generate_sales_report as tool_func

    result = tool_func.invoke({})

    assert isinstance(result, list)
    assert len(result) == 1
    assert "month" in result[0]
    assert "total_revenue" in result[0]

def test_tool_wrapper_create_sales_graph():
    from ..src.services.sales_agent import create_sales_graph as tool_func

    result = tool_func.invoke({"month": "2025-09"})

    assert isinstance(result, dict)
    assert result["type"] == "image"
    assert "data" in result

def test_sales_agent_initialization():
    from ..src.services.sales_agent import sales_agent
    assert sales_agent is not None
