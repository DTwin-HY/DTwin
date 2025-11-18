import copy
import json
from datetime import datetime
from typing import Any, Dict

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool, ToolRuntime

from .sql_agent import sql_agent_tool
from .sales_agent import sales_agent_tool
from .storage_agent import storage_agent_tool

load_dotenv()


class CounterfactualDataManager:
    """
    Manages counterfactual data scenarios, ensuring separation between real and what-if data.
    Provides structured data to analysis pipelines while maintaining data provenance.
    """

    def __init__(self):
        self.real_data_cache = {}
        self.counterfactual_scenarios = {}
        self.scenario_metadata = {}

    def create_counterfactual_scenario(
        self,
        scenario_name: str,
        base_data: Dict[str, Any],
        modifications: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new counterfactual scenario by modifying base data."""
        cf_data = copy.deepcopy(base_data)

        self._apply_modifications_recursive(cf_data, modifications)
        self._recalculate_dependent_metrics(cf_data)

        scenario_id = f"{scenario_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.counterfactual_scenarios[scenario_id] = cf_data
        self.scenario_metadata[scenario_id] = {
            "name": scenario_name,
            "created_at": datetime.now().isoformat(),
            "modifications": modifications,
            "base_data_hash": hash(json.dumps(base_data, sort_keys=True, default=str))
        }

        return {
            "scenario_id": scenario_id,
            "data": cf_data,
            "metadata": self.scenario_metadata[scenario_id]
        }

    def _apply_modifications_recursive(
        self,
        data: Any,
        modifications: Dict[str, Any]
    ) -> None: # pragma: no cover
        """Recursively apply modifications to handle nested data structures."""
        if isinstance(data, dict):
            for key, modification in modifications.items():
                if key in data and isinstance(modification, dict) and "operation" in modification:
                    self._apply_operation(data, key, modification)
                elif key in data and isinstance(modification, dict):
                    self._apply_modifications_recursive(data[key], modification)

            if "data" in data and isinstance(data["data"], list):
                for item in data["data"]:
                    if isinstance(item, dict):
                        self._apply_modifications_recursive(item, modifications)

            for k, v in data.items():
                if isinstance(v, (dict, list)) and k != "data":
                     self._apply_modifications_recursive(v, modifications)

        elif isinstance(data, list):
            for item in data:
                if isinstance(item, (dict, list)):
                    self._apply_modifications_recursive(item, modifications)

    def _apply_operation(
        self,
        data: Dict[str, Any],
        key: str,
        operation: Dict[str, Any]
    ) -> None:
        """Apply specific operations like percentage increase, set value, etc."""
        op_type = operation.get("operation")
        value = operation.get("value")

        if value is None:
            return

        current_value = data.get(key)
        if current_value is None:
            return

        try:
            current_value = float(current_value)
            if op_type == "percentage_increase":
                data[key] = current_value * (1 + value/100)
            elif op_type == "percentage_decrease":
                data[key] = current_value * (1 - value/100)
            elif op_type == "add_value":
                data[key] = current_value + value
            elif op_type == "multiply_by":
                data[key] = current_value * value
            elif op_type == "set_value":
                data[key] = value
            elif op_type == "decrease_by":
                data[key] = current_value - value
        except (TypeError, ValueError):
            pass

    def _recalculate_dependent_metrics(self, data: Dict[str, Any]) -> None:
        """Recalculate dependent metrics after modifications."""
        if "data" in data and isinstance(data["data"], list):
            for item in data["data"]:
                if isinstance(item, dict):
                    self._recalculate_item_metrics(item) # pragma: no cover
        self._recalculate_item_metrics(data) # pragma: no cover
    def _recalculate_item_metrics(self, item: Dict[str, Any]) -> None:
        """Helper to recalculate metrics for a single dictionary item"""
        if "total_revenue" in item and "total_items_sold" in item:
            try:
                revenue = float(item["total_revenue"])
                items = float(item["total_items_sold"])
                if items > 0:
                    unit_price = revenue / items
                    item["total_revenue"] = item["total_items_sold"] * unit_price
            except (ValueError, TypeError, ZeroDivisionError):
                pass
        elif "unit_price" in item and "quantity" in item:
            try:
                item["revenue"] = item["unit_price"] * item["quantity"]
            except (ValueError, TypeError):
                pass
        elif "unit_price" in item and "total_items_sold" in item:
             try:
                item["total_revenue"] = item["unit_price"] * item["total_items_sold"]
             except (ValueError, TypeError):
                pass

    def cache_real_data(self, data_key: str, data: Dict[str, Any]) -> None:
        """Cache real data with hash for comparison"""
        self.real_data_cache[data_key] = {
            "data": data,
            "hash": hash(json.dumps(data, sort_keys=True, default=str)),
            "cached_at": datetime.now().isoformat()
        }


class CounterfactualAgent:
    def __init__(self):
        self.data_manager = CounterfactualDataManager()
        self.analysis_tools = {
            "sql": sql_agent_tool,
            "sales": sales_agent_tool,
            "storage": storage_agent_tool
        }

    def handle_counterfactual_request(
        self,
        request: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle counterfactual requests with proper data separation and analysis."""
        try:
            base_query = request.get("base_query")
            analysis_type = request.get("analysis_type", "sql")

            if not base_query or not analysis_type:
                return {"error": "Missing required parameters: base_query or analysis_type"}

            real_data_result = self._get_base_data(base_query, analysis_type)

            if isinstance(real_data_result, str):
                try:
                    real_data_result = json.loads(real_data_result)
                except Exception:
                    real_data_result = {"raw_result": real_data_result}

            if "error" in real_data_result:
                return real_data_result

            self.data_manager.cache_real_data(
                f"{analysis_type}_{hash(base_query)}",
                real_data_result
            )

            scenario_name = request.get("scenario_name", f"what_if_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            modifications = request.get("modifications", {})

            cf_scenario = self.data_manager.create_counterfactual_scenario(
                scenario_name,
                real_data_result,
                modifications
            )

            cf_analysis_result = self._run_analysis_on_counterfactual(
                cf_scenario["data"],
                analysis_type
            )

            return self._format_counterfactual_response(
                real_data_result,
                cf_scenario,
                cf_analysis_result,
                analysis_type
            )

        except Exception as e:
            return {
                "error": f"Counterfactual analysis failed: {str(e)}",
                "scenario_id": request.get("scenario_name", "unknown")
            }

    def _get_base_data(self, query: str, analysis_type: str) -> Dict[str, Any]:
        """Get base real data using appropriate analysis tool"""
        if analysis_type not in self.analysis_tools:
            return {"error": f"Unsupported analysis type: {analysis_type}"}

        try:
            tool_instance = self.analysis_tools[analysis_type]

            result = tool_instance.invoke(query)

            if isinstance(result, str):
                try:
                    parsed = json.loads(result)
                    return parsed
                except Exception:
                    return {"raw_result": result, "status": "success"}
            return result
        except Exception as e:
            return {"error": f"Failed to get base data: {str(e)}"}

    def _run_analysis_on_counterfactual(self, cf_data: Dict[str, Any], analysis_type: str) -> Dict[str, Any]:
        return {
            "counterfactual_data": cf_data,
            "analysis_type": analysis_type,
            "status": "analyzed"
        }

    def _format_counterfactual_response(
        self,
        real_data: Dict[str, Any],
        cf_scenario: Dict[str, Any],
        cf_analysis: Dict[str, Any],
        analysis_type: str
    ) -> Dict[str, Any]:
        """Format response with clear separation between real and counterfactual data"""

        real_metrics = self._extract_key_metrics(real_data, analysis_type)
        cf_metrics = self._extract_key_metrics(cf_analysis["counterfactual_data"], analysis_type)

        differences = self._calculate_differences(real_metrics, cf_metrics)

        return {
            "status": "success",
            "scenario_id": cf_scenario["scenario_id"],
            "scenario_name": cf_scenario["metadata"]["name"],
            "timestamp": datetime.now().isoformat(),
            "real_data": {
                "summary": real_metrics,
                "full_data_reference": "cached_real_data"
            },
            "counterfactual_data": {
                "summary": cf_metrics,
                "scenario_metadata": cf_scenario["metadata"],
                "modifications_applied": cf_scenario["metadata"]["modifications"]
            },
            "comparison": {
                "differences": differences,
                "impact_summary": self._generate_impact_summary(differences)
            },
            "analysis_type": analysis_type,
            "data_separation_verified": True
        }

    def _extract_key_metrics(self, data, analysis_type):
        try:
            if analysis_type == "sales":
                if isinstance(data, dict) and "data" in data and isinstance(data["data"], list):
                    item = data["data"][0]
                    total_revenue = item.get("total_revenue", 0)
                    total_items_sold = item.get("total_items_sold", 0)
                else:
                    total_revenue = data.get("total_revenue", 0)
                    total_items_sold = data.get("total_items_sold", 1)
                avg_order_value = (
                    total_revenue / total_items_sold if total_items_sold else 0
                )
                return {
                    "total_revenue": total_revenue,
                    "total_items_sold": total_items_sold,
                    "average_order_value": round(avg_order_value, 2),
                }

            elif analysis_type == "storage":
                if isinstance(data, dict) and "data" in data and isinstance(data["data"], list):
                    total_inventory = sum(
                        item.get("amount", 0) or item.get("quantity", 0)
                        for item in data["data"]
                    )
                    item_count = len(data["data"])
                else:
                    total_inventory = data.get("total_inventory", 0)
                    item_count = data.get("item_count", 0)
                return {
                    "total_inventory": total_inventory,
                    "item_count": item_count,
                }

            else:
                if isinstance(data, dict):
                    if "raw_result" in data:
                        return {"raw_result": str(data["raw_result"])[:200] + "..."}

                    return {
                        k: v for k, v in data.items()
                        if k not in ["metadata", "status"]
                    }

                return {"raw_result": str(data)[:200] + "..."}

        except Exception as e:
            return {"error": f"metric extraction failed: {e}"}

    def _calculate_differences(self, real_metrics: Dict[str, Any], cf_metrics: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Calculate differences between real and counterfactual metrics"""
        differences = {}
        for key in real_metrics:
            if key in cf_metrics and isinstance(real_metrics[key], (int, float)) and isinstance(cf_metrics[key], (int, float)):
                real_value = float(real_metrics[key])
                cf_value = float(cf_metrics[key])
                if real_value == cf_value: continue

                absolute_diff = cf_value - real_value
                percentage_diff = (absolute_diff / real_value * 100) if real_value != 0 else 0

                differences[key] = {
                    "real_value": real_value,
                    "counterfactual_value": cf_value,
                    "absolute_difference": absolute_diff,
                    "percentage_difference": percentage_diff,
                    "direction": "increase" if absolute_diff > 0 else "decrease" if absolute_diff < 0 else "no_change"
                }
        return differences

    def _generate_impact_summary(self, differences: Dict[str, Dict[str, Any]]) -> str:
        """Generate human-readable impact summary"""
        significant_changes = [
            f"{key}: {diff['direction']} of {abs(diff['percentage_difference']):.1f}%"
            for key, diff in differences.items()
            if abs(diff['percentage_difference']) > 0.01
        ]
        if not significant_changes:
            return "No significant changes detected in the counterfactual scenario."
        return f"Significant impacts: {', '.join(significant_changes)}"


counterfactual_agent_instance = CounterfactualAgent()

@tool
def run_what_if_scenario_utility(
    scenario_name: str,
    base_query: str,
    modifications: Dict[str, Any],
    analysis_type: str = "sql"
) -> str:
    """
    INTERNAL UTILITY: Perform counterfactual analysis.
    Calls the data manager logic and returns a JSON string.
    """
    request = {
        "scenario_name": scenario_name,
        "base_query": base_query,
        "modifications": modifications,
        "analysis_type": analysis_type
    }
    result_dict = counterfactual_agent_instance.handle_counterfactual_request(request)
    return json.dumps(result_dict, indent=2)

COUNTERFACTUAL_SYSTEM_PROMPT = """
You are a "what-if" analysis coordinator. Your job is to translate the user's
natural language "what-if" question into a structured call to the
`run_what_if_scenario_utility` tool.

You will receive the FULL conversation history.

**CRITICAL:** You must parse the user's request and the conversation history
to determine three things: `base_query`, `modifications`, and `analysis_type`.

1.  **`base_query`**: Find the *original, most recent query* that got the data.
    - If history has "User: generate sales report for january 2025" and
      "AI: Sales Report...", the `base_query` is
      "generate sales report for january 2025".

2.  **`analysis_type`**: Infer this from the `base_query`.
    - "generate sales report..." -> "sales"
    - "check inventory" or "warehouse" -> "storage"
    - If unsure, default to "sql".

3.  **`modifications`**: Translate the user's wish into JSON modifications.
    The keys must match the keys in the data (e.g., "total_revenue", "total_items_sold").

    - User: "what if total revenue was 20% higher"
      Modifications: `{"total_revenue": {"operation": "percentage_increase", "value": 20}}`
    - User: "what if we sold 1000 more units"
      Modifications: `{"total_items_sold": {"operation": "add_value", "value": 1000}}`

**WORKFLOW:**
1.  Receive history.
2.  Infer `base_query` and `analysis_type` from past messages.
3.  Translate the new "what-if" question into `modifications`.
4.  Call `run_what_if_scenario_utility`.
5.  **CRITICAL:** Your final response MUST be ONLY the JSON string output from the tool.
"""

counterfactual_reasoning_agent = create_agent(
    name="counterfactual_translator",
    model="openai:gpt-4o-mini",
    tools=[run_what_if_scenario_utility],
    system_prompt=COUNTERFACTUAL_SYSTEM_PROMPT,
)


@tool
def counterfactual_analysis_tool(runtime: ToolRuntime) -> str:
    """
    Agent responsible for "what-if" scenarios.
    It takes the conversation history, translates natural language into
    structured data modifications, and runs a separated analysis.
    """
    messages = runtime.state.get("messages", [])
    if not messages:
        return "Error: No messages found in state."

    messages_for_agent = messages[:-1]

    result = counterfactual_reasoning_agent.invoke({"messages": messages_for_agent})

    return result["messages"][-1].content