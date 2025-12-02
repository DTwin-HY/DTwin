import os
from typing import Any, Dict, TypedDict

import pandas as pd
from dotenv import load_dotenv
from langgraph.graph import END, StateGraph
from sklearn.linear_model import LinearRegression

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


class ToolState(TypedDict, total=False):
    df: dict
    y_value: str
    results: Dict[str, Any]
    errors: list[str]


def validation_node(state: ToolState) -> ToolState:
    df = pd.DataFrame(state.get("df"))
    if df is None or df.empty:
        state["errors"] = ["No data provided."]
        return state

    return state


def analysis_node(state: ToolState) -> ToolState:
    if state.get("errors"):
        return state
    df = pd.DataFrame(state["df"])

    y_col = state.get("y_value")

    numeric_cols = df.select_dtypes(include=["number", "boolean"]).columns.tolist()

    if not y_col:
        if not numeric_cols:
            state["errors"] = ["No numeric columns available for analysis"]
            return state
        if not y_col:
            y_col = numeric_cols[0]
    feature_cols = [c for c in numeric_cols if c != y_col]

    X = df.loc[:, feature_cols].astype(float)
    y = df.loc[:, y_col].astype(float)

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
