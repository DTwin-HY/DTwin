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
    database_data: str,
    runtime: ToolRuntime,
    weather_data: str
) -> str:
    """
    Create a DataFrame by combining sales data and weather data, then save as CSV.
    
    Parameters:
    database_data: JSON string with database data from sql agent
    weather_data: JSON string with weather data from mcp agent
    
    Returns path to the saved CSV file.
    """
    if not os.path.exists("dataframes"):
        os.makedirs("dataframes")
    file_path = f"dataframes/dataframe_{runtime.tool_call_id}.csv"
    print("weather_data type in create_dataframe_tool:", type(weather_data))
    print("weather_data[0] type in create_dataframe_tool:", type(weather_data[0]))
    print("weather_data in create_dataframe_tool:", weather_data)
    print("database data in create_dataframe_tool:", database_data)
    try:
        # Parse both JSON inputs
        database_data_json = json.loads(database_data) if isinstance(database_data, str) else database_data
        weather_data_json = json.loads(weather_data) if isinstance(weather_data, str) else weather_data

        # Create DataFrames
        database_data_df = pd.DataFrame(database_data_json)
        weather_data_df = pd.DataFrame(weather_data_json)
        print("tässä df weather ",weather_data_df)
        print("tässä df_sales ",database_data_df)

        # # Convert timestamp to date for merging
        # if 'timestamp' in df_sales.columns:
        #     df_sales['date'] = pd.to_datetime(df_sales['timestamp']).dt.date
        
        # # Convert weather date string to date
        # if 'date' in df_weather.columns:
        #     df_weather['date'] = pd.to_datetime(df_weather['date']).dt.date
        
        # Merge on date
        df_final = pd.merge(
            database_data_df, 
            weather_data_df, 
            on='Date', 
            how='left'
        )
        print("mergetty df tässä ",df_final)

        # df_final = database_data_df

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
        "You are an agent responsible for creating dataframes for sales analysis. "
        "Weather data is fetched from mcp_agent_tool. NOT DATABASE. "
        "Dataframes are created from REAL DATA THAT IS ALRADY IN THE DATABASE. USE THE SQL AGENT TOOL TO FETCH THE DATA OTHER THAN WEATHER DATA. "
        "When asked to create a dataframe: "
        "1. First, use sql_agent_tool to fetch the required data from the database. "
        "   Ask the SQL agent to return data as JSON."
        "   Give the prompt in natural language to the sql agent, it will generate the query"
        "2. If user asks for weather data, fetch it from mcp_agent_tool."
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