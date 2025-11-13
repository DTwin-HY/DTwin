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
    df = pd.DataFrame({"sales": sales, "price": price, "customers": customers, "sunny": sunny})
    print("df from create product sales data:", df)
    return str(df)

@tool
def create_dataframe_tool(prompt: str, runtime: ToolRuntime) -> Command:
    """Tool to create a dataframe and add it to the state."""
    result = create_product_sales_data()
    print("result from create_dataframe_tool:", result)
    return Command(update={
        "dataframe": result,
        "messages": [
            ToolMessage(
                content="Dataframe created and added to state",
                tool_call_id=runtime.tool_call_id
            )
        ]
    })