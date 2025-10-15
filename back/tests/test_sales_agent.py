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

def test_create_sales_graph_error():
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