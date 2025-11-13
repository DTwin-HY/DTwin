import os

from langchain.messages import ToolMessage
from langchain.tools import tool, ToolRuntime
from langgraph.types import Command
import numpy as np
import pandas as pd

from ..utils.csv_to_pd import csv_to_pd #temp

def create_product_sales_data(rows: int = 30):
    """Generate (by default 30 rows of) daily product data for simulation testing."""
    np.random.seed(42)  # same numbers each run, for reproducibility

    sales = np.random.randint(70, 200, size=rows)
    price = np.round(np.random.uniform(10.0, 15.0, size=30), 2)
    customers = np.random.randint(40, 100, size=rows)
    sunny = np.random.choice([0, 1], size=rows).astype(bool)

    # Combine into a dataframe

    df = pd.DataFrame(
        {
            "sales": sales,
            "price": price,
            "customers": customers,
            "sunny": sunny,
        }
    )
    print("create_product_sales_data() generated DataFrame:", df.shape)
    return df


@tool
def create_dataframe_tool(prompt: str, runtime: ToolRuntime) -> Command:
    """Create a pd dataframe and save it to a csv file for other agents."""
    df = create_product_sales_data()
    df_json = df.to_json(orient="records")
    if not os.path.exists("dataframes"):
        os.makedirs("dataframes")
    file_path = f"dataframes/dataframe_{runtime.tool_call_id}.csv"
    df.to_csv(file_path, index=False)

    print(f"[create_array_tool_file] DataFrame saved to {file_path}, shape {df.shape}")

    return Command(update={
        "dataframe": df_json,
        "messages": [
            ToolMessage(
                content=f"Pd dataframe saved to file: {file_path}",
                tool_call_id=runtime.tool_call_id
            )
        ]
    })

@tool
def json_dataframe_test_tool(runtime:ToolRuntime) -> str:
    """
        Tool to check the json dataframe. Used in development only.
        Parameters:
        dataframe_path: str : path to the dataframe csv file.
    """
    dataframe = runtime.state.get("dataframe", None) #pragma: no cover
    dataframe = pd.read_json(dataframe, orient="records")
    return str(dataframe) #pragma: no cover

@tool
def state_dataframe_test_tool(dataframe_path: str) -> str:
    """Tool to check the value of dataframe in the state. Used in development only."""
    path = dataframe_path
    print("path:", path) #pragma: no cover
    pd = csv_to_pd(path) #pragma: no cover
    print(pd)
    return pd #pragma: no cover
