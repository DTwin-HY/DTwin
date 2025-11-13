import os
from typing import Any, Dict, List, TypedDict

import pandas as pd
from dotenv import load_dotenv
from langchain_core.tools import StructuredTool
from langgraph.graph import END, StateGraph
from sklearn.linear_model import LinearRegression

from src.data_scripts.data_analysis_test_data import create_product_sales_data

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


class ToolState(TypedDict, total=False):
    df: pd.DataFrame
    results: Dict[str, Any]
    errors: list[str]


def validation_node(state: ToolState) -> ToolState:
    df = state.get("df")
    if df is None or df.empty:
        state["errors"] = ["No data provided."]
        return state

    expected_data = {"sales", "price", "customers", "sunny"}
    missing_data = expected_data - set(df.columns)

    if missing_data:
        state["errors"] = [f"Missing columns: {missing_data}"]
    return state


def analysis_node(state: ToolState) -> ToolState:
    if state.get("errors"):
        return state
    df = state["df"]

    # How much price, weather and customer count affect sales
    X = df[["price", "sunny", "customers"]]
    y = df["sales"]
    model = LinearRegression().fit(X, y)

    state["results"] = {
        # How much predicted sales changes if variable changes by one unit
        "coefficients": {
            col: float(val) for col, val in zip(X.columns, model.coef_)
        },  # Cast to floats for cleaner print
        "intercept": float(model.intercept_),
        "r2_score": float(model.score(X, y)),
    }
    return state


def build_lin_reg_graph():
    graph = StateGraph(ToolState)
    graph.add_node("validate", validation_node)
    graph.add_node("analysis", analysis_node)
    graph.set_entry_point("validate")
    graph.add_edge("validate", "analysis")
    graph.add_edge("analysis", END)
    return graph.compile()
