import sys
from unittest.mock import MagicMock

sys.modules['langgraph'] = MagicMock()
sys.modules['langgraph.prebuilt'] = MagicMock()
sys.modules['langchain_core'] = MagicMock()
sys.modules['langchain_core.tools'] = MagicMock()
sys.modules['langchain_core.messages'] = MagicMock()

import os
import pytest
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

"""
import pytest
import base64
from unittest.mock import MagicMock
from ..src.services.sales_agent import SalesAgent


@pytest.fixture
def mock_sales_agent():
    mock_tool = MagicMock()

    fake_image_b64 = base64.b64encode(b"fake_image_bytes").decode("utf-8")
    mock_tool.create_sales_graph.return_value = {
        "status": "success",
        "type": "image",
        "format": "png",
        "data": fake_image_b64,
        "caption": "Daily Sales Revenue for 2025-09"
    }

    agent = SalesAgent(mock_tool)
    return agent, mock_tool

def test_create_sales_graph_success(mock_sales_agent):
    agent, mock_tool = mock_sales_agent
    month = "2025-09"

    result = agent.handle_request({"task": "create_graph", "month": month})

    assert isinstance(result, dict)
    assert result["status"] == "success"
    assert result["type"] == "image"
    assert result["format"] == "png"
    assert month in result["caption"]

    image_bytes = base64.b64decode(result["data"])
    assert image_bytes == b"fake_image_bytes"

    mock_tool.create_sales_graph.assert_called_once_with(month)

#def test_create_sales_graph_error():
    mock_tool = MagicMock()
    mock_tool.create_sales_graph.return_value = {
        "status": "error",
        "message": "No sales data for 3000-01"
    }
    agent = SalesAgent(mock_tool)
    month = "3000-01"

    result = agent.handle_request({"task": "create_graph", "month": month})

    assert isinstance(result, dict)
    assert result["status"] == "error"
    assert "No sales data" in result["message"]

    mock_tool.create_sales_graph.assert_called_once_with(month)
"""