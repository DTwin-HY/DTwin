import os
import json

import pandas as pd
from langchain.messages import HumanMessage
from langchain.tools import ToolRuntime, tool
from langchain.agents import create_agent

from ..utils.csv_to_pd import csv_to_pd  # temp
from .sql_agent import sql_agent_tool
from .mcp_client import mcp_agent_tool

@tool
def create_dataframe_tool(
    sales_data: str,
    customer_data: str,
    runtime: ToolRuntime,
    weather_data: str
) -> str:
    """
    Create a DataFrame by combining sales data and weather data, then save as CSV.
    
    Parameters:
    sales_data: JSON string with database data from sql agent
    customer_data: JSON string with customer data from sql agent
    
    Returns path to the saved CSV file.
    """
    if not os.path.exists("dataframes"):
        os.makedirs("dataframes")
    file_path = f"dataframes/dataframe_{runtime.tool_call_id}.csv"
    # print("weather_data type in create_dataframe_tool:", type(weather_data))
    # print("weather_data[0] type in create_dataframe_tool:", type(weather_data[0]))
    print("weather_data in create_dataframe_tool:", weather_data)
    print("sales data in create_dataframe_tool:", sales_data)
    print("customer data in create_dataframe_tool:", customer_data)
    try:
        # Parse both JSON inputs
        sales_data_json = json.loads(sales_data) if isinstance(sales_data, str) else sales_data
        customer_data_json = json.loads(customer_data) if isinstance(customer_data, str) else customer_data
        weather_data_json = json.loads(weather_data) if isinstance(weather_data, str) else weather_data

        # Create DataFrames
        sales_data_df = pd.DataFrame(sales_data_json)
        customer_data_df = pd.DataFrame(customer_data_json)
        weather_data_df = pd.DataFrame(weather_data_json)
        print("tässä df weather ",weather_data_df)
        print("tässä df_sales ",sales_data_df)
        print("tässä df_customer ",customer_data_df)

        df_tmp = pd.merge(
            sales_data_df,
            weather_data_df,
            on='date',
            how='left'
        )

        df_final = pd.merge(
            df_tmp,
            customer_data_df,
            on='date',
            how='left'
        )

        print("mergetty df tässä ",df_final)

        # Save to CSV
        df_final.to_csv(file_path, index=False, sep=";", encoding="utf-8-sig")
        
        print(f"[create_dataframe_tool] Combined DataFrame saved to {file_path}, shape {df_final.shape}")
        return f"DataFrame created and saved to: {file_path}"
        
    except Exception as e:
        print(f"[create_dataframe_tool] Error: {e}")
        return f"Error creating DataFrame: {str(e)}"

dataframe_agent = create_agent(
    name="dataframe_agent",
    model="openai:gpt-4o-mini",
    tools=[sql_agent_tool, create_dataframe_tool, mcp_agent_tool],
    system_prompt=(
        "You are an agent responsible for creating dataframe for simulation agent. "
        "Weather data is fetched from mcp_agent_tool. NOT DATABASE. "
        "Dataframes are created from real data. Fetch all other data than weather using the sql_agent_tool ONLY. "
        "Set date column as 'date' in all data fetched from database. "
        "Make the dataframe columns from the prompt that the user gives. "
        "When asked to create a dataframe: "
        "1. First, use sql_agent_tool to fetch the required data from the database. "
        "   Ask the SQL agent to return data as JSON." 
        "   ONLY ACCEPT JSON AS RETURN DATA FROM SQL AGENT."
        "   Give the prompt in natural language to the sql_agent_tool, it will generate the query"
        "2. If user asks for weather data, fetch it from mcp_agent_tool."
        "3. Return the file path to the user."
        " DO NOT MAKE UP ANY DATA YOURSELF"
    ),
)

@tool
def dataframe_agent_tool(prompt: str) -> str:
    """
    Dataframe creation agent tool. This tool fetches the data needed to create a dataframe
    by invoking the dataframe_agent.
    The dataframe_agent first fetches the data from the database using sql_agent_tool,
    then fetches weather data using mcp_agent_tool, and finally creates the dataframe.
    SO IT ONLY NEEDS THE PROMPT TO CREATE THE DATAFRAME AND NOT ANY DATA
    Parameters:
    prompt: str : The prompt to create the dataframe.
    Returns: str : The result of the dataframe creation.
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