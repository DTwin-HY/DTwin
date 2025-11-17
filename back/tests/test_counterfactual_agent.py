import pytest
from unittest.mock import MagicMock, patch

with patch("langchain.agents.create_agent"), \
     patch("dotenv.load_dotenv"):
    from back.src.services.counterfactual_agent import (
        CounterfactualDataManager,
        CounterfactualAgent,
    )

@pytest.fixture
def data_manager():
    return CounterfactualDataManager()

def test_apply_operation_basic_math(data_manager):
    data = {"revenue": 100.0, "count": 10}
    data_manager._apply_operation(data, "revenue", {"operation": "percentage_increase", "value": 20})
    assert data["revenue"] == 120.0
    data_manager._apply_operation(data, "count", {"operation": "add_value", "value": 5})
    assert data["count"] == 15
    data_manager._apply_operation(data, "revenue", {"operation": "set_value", "value": 500})
    assert data["revenue"] == 500.0
    data_manager._apply_operation(data, "count", {"operation": "multiply_by", "value": 2})
    assert data["count"] == 30
    data_manager._apply_operation(data, "count", {"operation": "decrease_by", "value": 10})
    assert data["count"] == 20
    data_manager._apply_operation(data, "revenue", {"operation": "percentage_decrease", "value": 50})
    assert data["revenue"] == 250.0

def test_apply_operation_edge_cases(data_manager):
    data = {"revenue": 100}
    data_manager._apply_operation(data, "missing_key", {"operation": "add_value", "value": 10})
    assert "missing_key" not in data
    data_manager._apply_operation(data, "revenue", {"operation": "add_value", "value": None})
    assert data["revenue"] == 100
    data_broken = {"revenue": None}
    data_manager._apply_operation(data_broken, "revenue", {"operation": "add_value", "value": 10})
    assert data_broken["revenue"] is None
    data_str = {"revenue": "not_a_number"}
    data_manager._apply_operation(data_str, "revenue", {"operation": "add_value", "value": 10})
    assert data_str["revenue"] == "not_a_number"

def test_recursive_modification_global(data_manager):
    data = {
        "meta": {"version": 1},
        "summary": {"total_revenue": 100},
        "data": [
            {"product": "A", "revenue": 50},
            {"product": "B", "revenue": 50}
        ]
    }
    mods = {"revenue": {"operation": "add_value", "value": 10}}
    data_manager._apply_modifications_recursive(data, mods)
    assert data["data"][0]["revenue"] == 60
    assert data["data"][1]["revenue"] == 60

def test_create_counterfactual_scenario(data_manager):
    base = {"data": [{"revenue": 100}]}
    mods = {"revenue": {"operation": "add_value", "value": 50}}
    result = data_manager.create_counterfactual_scenario("test_scenario", base, mods)
    assert result["scenario_id"].startswith("test_scenario_")
    assert result["data"]["data"][0]["revenue"] == 150
    assert result["metadata"]["name"] == "test_scenario"
    assert base["data"][0]["revenue"] == 100

@pytest.fixture
def agent():
    return CounterfactualAgent()

def test_get_base_data(agent):
    mock_sql_tool = MagicMock()
    agent.analysis_tools["sql"] = mock_sql_tool
    mock_sql_tool.invoke.return_value = {"result": "ok"}
    res = agent._get_base_data("query", "sql")
    assert res == {"result": "ok"}
    mock_sql_tool.invoke.return_value = '{"result": "json"}'
    res = agent._get_base_data("query", "sql")
    assert res == {"result": "json"}
    mock_sql_tool.invoke.return_value = "Just a string"
    res = agent._get_base_data("query", "sql")
    assert res == {"raw_result": "Just a string", "status": "success"}
    mock_sql_tool.invoke.side_effect = Exception("Tool failed")
    res = agent._get_base_data("query", "sql")
    assert "error" in res
    res = agent._get_base_data("query", "unknown_type")
    assert "error" in res

def test_extract_key_metrics(agent):
    data_sales = {"data": [{"total_revenue": 100, "total_items_sold": 10}]}
    metrics = agent._extract_key_metrics(data_sales, "sales")
    assert metrics["total_revenue"] == 100
    assert metrics["average_order_value"] == 10.0
    data_sales_flat = {"total_revenue": 200, "total_items_sold": 20}
    metrics = agent._extract_key_metrics(data_sales_flat, "sales")
    assert metrics["total_revenue"] == 200
    data_storage = {"data": [{"amount": 50}, {"quantity": 50}]}
    metrics = agent._extract_key_metrics(data_storage, "storage")
    assert metrics["total_inventory"] == 100
    assert metrics["item_count"] == 2
    data_storage_direct = {"total_inventory": 500}
    metrics = agent._extract_key_metrics(data_storage_direct, "storage")
    assert metrics["total_inventory"] == 500
    data_sql = {"some_metric": 123, "metadata": "ignore"}
    metrics = agent._extract_key_metrics(data_sql, "sql")
    assert metrics["some_metric"] == 123
    assert "metadata" not in metrics
    data_raw = "Just text"
    metrics_raw = agent._extract_key_metrics(data_raw, "sql")
    assert "raw_result" in metrics_raw

def test_calculate_differences(agent):
    real = {"rev": 100, "static": 50}
    cf = {"rev": 120, "static": 50}
    diff = agent._calculate_differences(real, cf)
    assert "static" not in diff
    assert diff["rev"]["absolute_difference"] == 20
    assert diff["rev"]["percentage_difference"] == 20.0
    assert diff["rev"]["direction"] == "increase"

def test_generate_impact_summary(agent):
    diff = {"rev": {"direction": "increase", "percentage_difference": 10.5},
            "tiny": {"direction": "decrease", "percentage_difference": 0.001}}
    summary = agent._generate_impact_summary(diff)
    assert "rev: increase of 10.5%" in summary
    assert "tiny" not in summary
    assert "No significant changes" in agent._generate_impact_summary({})

def test_handle_counterfactual_request_flow(agent):
    with patch.object(agent, '_get_base_data') as mock_get:
        mock_get.return_value = {"data": [{"total_revenue": 100, "total_items_sold": 10}]}
        request = {
            "base_query": "sales report",
            "analysis_type": "sales",
            "modifications": {"total_revenue": {"operation": "add_value", "value": 50}}
        }
        response = agent.handle_counterfactual_request(request)
        assert response["status"] == "success"
        assert response["real_data"]["summary"]["total_revenue"] == 100
        assert response["counterfactual_data"]["summary"]["total_revenue"] == 150
        assert response["comparison"]["differences"]["total_revenue"]["absolute_difference"] == 50

def test_handle_counterfactual_request_errors(agent):
    assert "error" in agent.handle_counterfactual_request({})
    with patch.object(agent, '_get_base_data', return_value={"error": "db fail"}):
        res = agent.handle_counterfactual_request({"base_query": "q", "analysis_type": "sql"})
        assert res["error"] == "db fail"