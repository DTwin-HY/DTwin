import pytest
import json
from unittest.mock import MagicMock, patch

with patch("langchain.agents.create_agent"), \
     patch("dotenv.load_dotenv"):
    from back.src.services.counterfactual_agent import (
        CounterfactualDataManager,
        CounterfactualAgent,
        run_what_if_scenario_utility,
        counterfactual_analysis_tool,
        counterfactual_reasoning_agent
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

def test_recalculate_dependent_metrics_coverage(data_manager):
    """Test specific math logic in _recalculate_item_metrics that wasn't covered."""
    data_case_1 = {
        "data": [
            {"unit_price": 10.0, "quantity": 5}
        ]
    }
    data_manager._recalculate_dependent_metrics(data_case_1)
    assert data_case_1["data"][0]["revenue"] == 50.0

    data_case_2 = {
        "data": [
            {"unit_price": 20.0, "total_items_sold": 4}
        ]
    }
    data_manager._recalculate_dependent_metrics(data_case_2)
    assert data_case_2["data"][0]["total_revenue"] == 80.0

    data_case_3 = {
        "data": [
            {"total_revenue": 100.0, "total_items_sold": 10.0}
        ]
    }
    data_manager._recalculate_dependent_metrics(data_case_3)
    assert data_case_3["data"][0]["total_revenue"] == 100.0

    data_zero = {
        "data": [
            {"total_revenue": 100.0, "total_items_sold": 0}
        ]
    }

    data_manager._recalculate_dependent_metrics(data_zero)
    assert data_zero["data"][0]["total_revenue"] == 100.0

    data_bad = {
        "data": [
            {"unit_price": "invalid", "quantity": 5}
        ]
    }

    data_manager._recalculate_dependent_metrics(data_bad)
    assert data_bad["data"][0]["unit_price"] == "invalid"


def test_cache_real_data(data_manager):
    """Test that real data is cached with correct structure."""
    data = {"some": "data"}
    data_manager.cache_real_data("key1", data)

    cached = data_manager.real_data_cache["key1"]
    assert cached["data"] == data
    assert "hash" in cached
    assert "cached_at" in cached


def test_tool_run_what_if_scenario_utility():
    """Test the @tool function for running scenarios."""
    with patch("back.src.services.counterfactual_agent.counterfactual_agent_instance") as mock_agent_instance:
        mock_agent_instance.handle_counterfactual_request.return_value = {
            "status": "success",
            "scenario_id": "123"
        }
        try:
            result_json = run_what_if_scenario_utility.func(
                scenario_name="Test",
                base_query="query",
                modifications={}
            )
        except AttributeError:
            result_json = run_what_if_scenario_utility(
                scenario_name="Test",
                base_query="query",
                modifications={}
            )

        result = json.loads(result_json)
        assert result["status"] == "success"
        assert result["scenario_id"] == "123"

        mock_agent_instance.handle_counterfactual_request.assert_called_once()


def test_tool_counterfactual_analysis_tool():
    """Test the main orchestration tool."""
    mock_runtime = MagicMock()

    mock_runtime.state = {}
    res_empty = counterfactual_analysis_tool.func(mock_runtime)
    assert "Error" in res_empty

    mock_runtime.state = {
        "messages": [
            MagicMock(content="User query"),
            MagicMock(content="Current message")
        ]
    }

    with patch.object(counterfactual_reasoning_agent, "invoke") as mock_invoke:
        mock_response_msg = MagicMock()
        mock_response_msg.content = '{"tool_output": "success"}'

        mock_invoke.return_value = {
            "messages": [
                MagicMock(),
                mock_response_msg
            ]
        }

        res = counterfactual_analysis_tool.func(mock_runtime)
        assert res == '{"tool_output": "success"}'
        mock_invoke.assert_called_once()

def test_agent_handle_request_parse_raw_string(agent):
    """Test handling where real data is returned as a JSON string from the tool."""
    with patch.object(agent, '_get_base_data') as mock_get:
        mock_get.return_value = '{"data": [{"total_revenue": 500}]}'

        request = {
            "base_query": "q",
            "analysis_type": "sales",
            "modifications": {"total_revenue": {"operation": "add_value", "value": 100}}
        }

        response = agent.handle_counterfactual_request(request)

        assert response["status"] == "success"
        assert response["real_data"]["summary"]["total_revenue"] == 500
        assert response["counterfactual_data"]["summary"]["total_revenue"] == 600

def test_agent_handle_request_exception_handling(agent):
    """Test the top-level try/except block in handle_counterfactual_request."""
    with patch.object(agent, '_get_base_data', side_effect=Exception("Critical Failure")):
        request = {"base_query": "q", "analysis_type": "sql"}
        response = agent.handle_counterfactual_request(request)
        assert "error" in response
        assert "Critical Failure" in response["error"]

def test_recalculate_metrics_exceptions(data_manager):
    """Force exception blocks in _recalculate_item_metrics"""
    item_fail_2 = {"unit_price": "not_a_num", "quantity": "also_not_num"}
    data_manager._recalculate_item_metrics(item_fail_2)
    assert "revenue" not in item_fail_2

    item_fail_3 = {"unit_price": "not_a_num", "total_items_sold": "also_not_num"}
    data_manager._recalculate_item_metrics(item_fail_3)
    assert "total_revenue" not in item_fail_3

def test_recursive_nested_list_custom_key(data_manager):
    """Test recursion into a list that is NOT named 'data'."""
    data = {
        "other_list": [
            {"val": 10},
            {"val": 20}
        ]
    }
    mods = {"val": {"operation": "add_value", "value": 5}}
    data_manager._apply_modifications_recursive(data, mods)
    assert data["other_list"][0]["val"] == 15
    assert data["other_list"][1]["val"] == 25

def test_handle_request_returns_raw_string_structure(agent):
    """
    Force _get_base_data to return a plain string that IS NOT json parsable
    to test the 'if isinstance(real_data_result, str)' block in handle_counterfactual_request
    assuming _get_base_data could theoretically return a raw string.
    """
    with patch.object(agent, '_get_base_data') as mock_get:
        mock_get.return_value = "Raw SQL Result String"


        request = {"base_query": "q", "analysis_type": "sql"}
        response = agent.handle_counterfactual_request(request)

        assert response["real_data"]["summary"]["raw_result"].startswith("Raw SQL Result String")

def test_extract_metrics_generic_failure(agent):
    """Test the generic Exception catch in _extract_key_metrics."""
    class AngryObject:
        def __getitem__(self, item):
            raise Exception("I refuse")

    res = agent._extract_key_metrics(AngryObject(), "sales")
    assert "error" in res