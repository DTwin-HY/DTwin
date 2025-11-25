import os
import json

import numpy as np
import pandas as pd
from langchain.messages import ToolMessage, HumanMessage
from langchain.tools import ToolRuntime, tool
from langgraph.types import Command
from langchain.agents import create_agent

from ..utils.csv_to_pd import csv_to_pd  # temp
from .sql_agent import sql_agent_tool

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
    json_data: str,
    runtime: ToolRuntime
) -> str:
    """
    Create a DataFrame from JSON data and save as CSV.
    
    Parameters:
    json_data: JSON string containing array of objects with the data
    
    Returns path to the saved CSV file.
    """
    if not os.path.exists("dataframes"):
        os.makedirs("dataframes")
    file_path = f"dataframes/dataframe_{runtime.tool_call_id}.csv"
    try:
        # Parse JSON data
        data = json.loads(json_data) if isinstance(json_data, str) else json_data
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Save to CSV
        df.to_csv(file_path, index=False, sep=";", encoding="utf-8-sig")
        
        print(f"[create_dataframe_tool] DataFrame saved to {file_path}, shape {df.shape}")
        return f"DataFrame created and saved to: {file_path}"
        
    except Exception as e:
        print(f"[create_dataframe_tool] Error: {e}, creating mock data")
        df = create_product_sales_data()
        df.to_csv(file_path, index=False, sep=";", encoding="utf-8-sig")
        return f"Error creating DataFrame from JSON. Created mock data instead at: {file_path}"

dataframe_agent = create_agent(
    name="dataframe_agent",
    model="openai:gpt-4o-mini",
    tools=[sql_agent_tool, create_dataframe_tool],
    system_prompt=(
        "You are an agent responsible for creating dataframes for sales analysis. "
<<<<<<< HEAD
        "Dataframes are created from REAL DATA THAT IS ALRADY IN THE DATABASE. USE THE SQL AGENT TOOL TO FETCH THE DATA. "
        "When asked to create a dataframe: "
        "1. First, use sql_agent_tool to fetch the required data from the database. "
        "   Ask the SQL agent to return data as JSON."
        "   Give the prompt in natural language to the sql agent, it will generate the query"
        "2. Then, pass the JSON result to create_dataframe_tool to save it as a CSV file. "
        "3. Return the file path to the user."
        " DO NOT MAKE UP ANY DATA YOURSELF"
=======
        "When asked to create a dataframe: "
        "1. First, use sql_agent_tool to fetch the required data from the database. "
        "   Ask the SQL agent to return data as JSON."
        "   Give the prompt in natural language to the sql agent, it will generate the query"
        "2. Then, pass the JSON result to create_dataframe_tool to save it as a CSV file. "
        "3. Return the file path to the user."
        " DO NOT MAKE UP ANY DATA YOURSELF"
    ),
)

@tool
def dataframe_agent_tool(prompt: str) -> str:
    """
    Wraps the dataframe_agent as a single tool.
    """
    result = dataframe_agent.invoke({"messages": [HumanMessage(content=prompt)]})
    return result["messages"][-1].content

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