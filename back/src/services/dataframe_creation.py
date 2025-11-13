import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.messages import HumanMessage, ToolMessage
from langchain.tools import tool, ToolRuntime
from langgraph.types import Command
from langchain.agents.middleware import AgentState
import numpy as np
import pandas as pd

def create_product_sales_data(rows: int = 30):
    """Generate (by default 30 rows of) daily product data for simulation testing."""
    np.random.seed(42)  # same numbers each run, for reproducibility

    sales = np.random.randint(70, 200, size=rows)
    price = np.round(np.random.uniform(10.0, 15.0, size=30), 2)
    customers = np.random.randint(40, 100, size=rows)
    sunny = np.random.choice([0, 1], size=rows).astype(bool)

    # Combine into a dataframe

    data = np.column_stack([sales, price, customers, sunny])
    print("create_product_sales_data() generated array of shape:", data.shape)
    return data

@tool
def create_array_tool_file(prompt: str, runtime: ToolRuntime) -> Command:
    """Create a NumPy array and save it to a .npy file for other agents."""
    arr = create_product_sales_data()
    file_path = "shared_sales_data.npy"
    np.save(file_path, arr)

    print(f"[create_array_tool_file] Array saved to {file_path}, shape {arr.shape}")

    return Command(update={
        "array_path": file_path,
        "messages": [
            ToolMessage(
                content=f"NumPy array saved to file: {file_path}",
                tool_call_id=runtime.tool_call_id
            )
        ]
    })
