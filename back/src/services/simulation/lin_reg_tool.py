from typing import Any, Dict, List

import pandas as pd
from langchain_core.tools import StructuredTool
from langchain.tools import tool, ToolRuntime
from langgraph.types import Command

from ...services.simulation.lin_reg_graph import build_lin_reg_graph


def csv_fetch(dataframe_path: str) -> str:
    """
    Tool to check the value of dataframe saved as csv. Used in development only.
    Parameters:
    dataframe_path: str : path to the dataframe csv file.
    """
    path = dataframe_path
    dataframe = pd.read_csv(path).to_dict() 
    print("fetched dataframe from csv file:\n", dataframe) 
    
    return dataframe


@tool
def lin_reg_tool(data_location: str) -> Dict[str, Any]:
    """Runs the linear regression simulation graph on given data. \n
    Expects a string with data location on file"""

    try:
        data = csv_fetch(data_location)
    except:
        return "Failed to load data."

    graph = build_lin_reg_graph()
    result = graph.invoke({"df": data})
    
    return result.get("results", {"errors": result.get("errors", [])})


if __name__ == "__main__":
    from src.data.data_analysis_test_data import create_product_sales_data

    df = create_product_sales_data()
    print("Generated sample data:")
    print(df.head())

    results = run_lin_reg_tool(df.to_dict(orient="records"))
    print("Simulation results:")
    print(results)
