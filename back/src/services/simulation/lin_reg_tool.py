from typing import Any, Dict, List

import pandas as pd
from langchain_core.tools import StructuredTool
from langchain.tools import tool

from ...services.simulation.lin_reg_graph import build_lin_reg_graph

@tool
def lin_reg_tool(data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Runs the linear regression simulation graph on given data. \n
    Expects data with columns: sales, sunny, price, customers"""
    df = pd.DataFrame(data)
    graph = build_lin_reg_graph()
    result = graph.invoke({"df": df})
    
    return result.get("results", {"errors": result.get("errors", [])})


#lin_req_tool = StructuredTool.from_function(
#    func=lin_reg_tool,
#    name="linear_regression_simulation",
#    description=(
#        "Run a linear regression simulation on product sales data. "
#        "Expects data with columns: sales, sunny, price, customers."
#    ),
#)
#

if __name__ == "__main__":
    from src.data.data_analysis_test_data import create_product_sales_data

    df = create_product_sales_data()
    print("Generated sample data:")
    print(df.head())

    results = run_lin_reg_tool(df.to_dict(orient="records"))
    print("Simulation results:")
    print(results)
