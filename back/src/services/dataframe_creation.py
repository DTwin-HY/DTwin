import os
import json

import pandas as pd
from langchain.messages import HumanMessage
from langchain.tools import ToolRuntime, tool
from langchain.agents import create_agent

from ..utils.csv_to_pd import csv_to_pd  # temp
from .sql_agent import sql_agent_tool
from ..utils.mock_weather import thirty_day_weather_mock
from .mcp_client import mcp_agent_tool

@tool
def weather_tool() -> str:
    """
    Tool to return weather data as JSON string.
    """
    return "error while fetching weather data"

@tool
def create_dataframe_tool(
    sales_json: str,
    runtime: ToolRuntime,
    weather_json: str = None
) -> str:
    """
    Create a DataFrame by combining sales data and weather data, then save as CSV.
    
    Parameters:
    sales_json: JSON string with sales data from database
    weather_json: JSON string with weather data from external API
    
    Returns path to the saved CSV file.
    """
    if not os.path.exists("dataframes"):
        os.makedirs("dataframes")
    file_path = f"dataframes/dataframe_{runtime.tool_call_id}.csv"
    
    print("creating dataframe")
    print(weather_json)
    try:
        # Parse both JSON inputs
        json_data = json.loads(sales_json) if isinstance(sales_json, str) else sales_json
        
        # Create DataFrames
        df_sales = pd.DataFrame(json_data)

        if weather_json:
            if weather_json == "MOCK_WEATHER":
                weather_json = json.dumps(thirty_day_weather_mock())
            else:
                weather_data = json.loads(weather_json) if isinstance(weather_json, str) else weather_json
                df_weather = pd.DataFrame(weather_data)

                # Convert timestamp to date for merging
                if 'timestamp' in df_sales.columns:
                    df_sales['date'] = pd.to_datetime(df_sales['timestamp']).dt.date
                
                # Convert weather date string to date
                if 'date' in df_weather.columns:
                    df_weather['date'] = pd.to_datetime(df_weather['date']).dt.date
                
                # Merge on date
                df_final = pd.merge(
                    df_sales, 
                    df_weather[['date', 'sunny']], 
                    on='date', 
                    how='left'
                )
        else:
            df_final = df_sales

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
    tools=[sql_agent_tool, create_dataframe_tool, weather_tool],
    system_prompt=(
        "You are an agent responsible for creating dataframes for sales analysis. "
        "Dataframes are created from REAL DATA THAT IS ALRADY IN THE DATABASE. USE THE SQL AGENT TOOL TO FETCH THE DATA. "
        "When asked to create a dataframe: "
        "1. First, use sql_agent_tool to fetch the required data from the database. "
        "   Ask the SQL agent to return data as JSON."
        "   Give the prompt in natural language to the sql agent, it will generate the query"
        "2. If user asks for weather data, fetch it from weather_tool as JSON."
        "3. Then, pass the JSON result to create_dataframe_tool to save it as a CSV file. If weather data is needed butnot provided, give \"MOCK_WEATHER\" as weather_json parameter."
        "4. Return the file path to the user."
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