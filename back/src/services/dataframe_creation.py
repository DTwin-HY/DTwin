import os

import numpy as np
import pandas as pd
from langchain.messages import ToolMessage
from langchain.tools import ToolRuntime, tool
from langgraph.types import Command

from ..utils.csv_to_pd import csv_to_pd  # temp


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
def create_dataframe_tool(
    prompt: str, runtime: ToolRuntime  # pylint: disable=unused-argument
) -> Command:
    """
    Create a pd dataframe and save it to a csv file for other agents.
    """
    df = create_product_sales_data()
    if not os.path.exists("dataframes"):
        os.makedirs("dataframes")
    file_path = f"dataframes/dataframe_{runtime.tool_call_id}.csv"
    df.to_csv(file_path, index=False)

    print(f"[create_array_tool_file] DataFrame saved to {file_path}, shape {df.shape}")

    return Command(
        update={
            "messages": [
                ToolMessage(
                    content=f"Pd dataframe saved to file: {file_path}",
                    tool_call_id=runtime.tool_call_id,
                )
            ]
        }
    )


@tool
def csv_dataframe_test_tool(dataframe_path: str) -> str:
    """
    Tool to check the value of dataframe saved as csv. Used in development only.
    Parameters:
    dataframe_path: str : path to the dataframe csv file.
    """
    try:
        path = dataframe_path  # pragma: no cover
        print("path:", path)  # pragma: no cover
        dataframe = csv_to_pd(path)  # pragma: no cover
        print("fetched dataframe from csv file:", dataframe)  # pragma: no cover
        return dataframe  # pragma: no cover
    except Exception as e:
        return f"Error fetching dataframe from csv file. {e}"  # pragma: no cover
