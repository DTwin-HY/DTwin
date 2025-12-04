import json
import os

import pandas as pd
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langchain.tools import ToolRuntime, tool
from datetime import datetime

from ..utils.csv_to_pd import csv_to_pd  # temp
from ..utils.logger import logger
from .mcp_client import mcp_agent_tool
from .sql_agent import sql_agent_tool


@tool
def create_dataframe_tool(
    sales_data: str, customer_data: str, weather_data: str, runtime: ToolRuntime
) -> str:
    """
    Create a DataFrame by combining sales data and weather data, then save as CSV.

    Args:
        sales_data: JSON string with database data from sql agent
        customer_data: JSON string with customer data from sql agent
        weather_data: JSON string with weather data from MCP agent

    Returns path to the saved CSV file.
    """
    if not os.path.exists("dataframes"):
        os.makedirs("dataframes")
    file_path = f"dataframes/dataframe_{runtime.tool_call_id}.csv"
    logger.debug("weather_data in create_dataframe_tool:", weather_data)
    logger.debug("sales data in create_dataframe_tool:", sales_data)
    logger.debug("customer data in create_dataframe_tool:", customer_data)
    try:
        # Parse both JSON inputs
        sales_data_json = json.loads(sales_data) if isinstance(sales_data, str) else sales_data
        customer_data_json = (
            json.loads(customer_data) if isinstance(customer_data, str) else customer_data
        )
        weather_data_json = (
            json.loads(weather_data) if isinstance(weather_data, str) else weather_data
        )

        # Create DataFrames
        sales_data_df = pd.DataFrame(sales_data_json)
        customer_data_df = pd.DataFrame(customer_data_json)
        weather_data_df = pd.DataFrame(weather_data_json)
        logger.debug("df weather ", weather_data_df)
        logger.debug("df_sales ", sales_data_df)
        logger.debug("df_customer ", customer_data_df)

        df_tmp = pd.merge(sales_data_df, weather_data_df, on="date", how="left")

        df_final = pd.merge(df_tmp, customer_data_df, on="date", how="left")

        logger.debug("merged df ", df_final)

        df_final.to_csv(file_path, index=False, sep=";", encoding="utf-8-sig")

        logger.info(
            f"[create_dataframe_tool] Combined DataFrame saved to {file_path}"
            f", shape {df_final.shape}"
        )
        return f"DataFrame created and saved to: {file_path}"

    except Exception as e:
        logger.error(f"[create_dataframe_tool] Error: {e}")
        return f"Error creating DataFrame: {str(e)}"



OLD_DF_SYSTEM_PROMPT = """
    You are an agent responsible for creating dataframe for simulation agent. 
    Weather data is fetched from mcp_agent_tool. NOT DATABASE. 
    Dataframes are created from real data. Fetch all other
    data than weather using the sql_agent_tool ONLY. 
    Set date column as 'date' in all data fetched from database. 
    Make the dataframe columns from the prompt that the user gives. 
    When asked to create a dataframe: 

    1. First, use sql_agent_tool to fetch the required data from the database. 
       Ask the SQL agent to return data as JSON.
       ONLY ACCEPT JSON AS RETURN DATA FROM SQL AGENT.
       Give the prompt in natural language to the sql_agent_tool, it will generate the query
    2. If user asks for weather data, fetch it from mcp_agent_tool.
    3. Return the file path to the user.
     DO NOT MAKE UP ANY DATA YOURSELF

    """

today = datetime.today().strftime('%Y-%m-%d')

DF_SYSTEM_PROMPT = f"""
        You are a data collection agent responsible for collating datasets on company and external data to be used in analysis.

        You have the following tools at your disposal:

        1. SQL Agent tool
        2. MCP Agent tool to retrieve weather data
        3. Create dataframe tool



        1. The SQL Agent should be used to query for internal company related datapoints such as sales metrics, customer amounts or other data points directly related to the company's internal database. Prompt the SQL agent using natural language, it 
        will write it's own query. Query the agent separately for customer and sales data.

        2. The MCP Agent is used to retrieve any weather based data points. If no location for weather data is provided, assume that the location is Helsinki, Finland.

        3. The create dataframe tool is to be used to formulate the final dataset into a pandas DataFrame-object
        which is stored as a .csv-file on file by the tool. The inputs to the dataframe tool should contain date 


        If the user prompt doesn't provide a date range, assume they want data for the last 7 days. Today is {today}.


        Example task:

        User prompt: "Create a dataset for linear regression that can be used to analyse the effect of sunny weather, prices, customer amounts on total sales. The date range is 30.11-1.12.2025"

        Step 1. Use the SQL agent to retrieve the internal data, i.e. product prices, customer amounts and total sales.
        Ask the SQL Agent to return data in JSON, if the returned data is not JSON convert it yourself.

        The JSON should be formatted as follows: 
        For sales data:
        {
            {
            "date":"2025-12-01",
            "sales":90049.98,
            "average_product_price":48.44
            },
        {
            "date":"2025-11-30",
            "sales":60609.08,
            "average_product_price":48.44
            },
        }

        For customer data:
        {
            {
            "date":"2025-12-01",
            "customer_amount":24700,
            },
        {
            "date":"2025-11-30",
            "customer_amounts":8900,
            },
        }


        DO NOT WRAP THE JSON AS A LIST.

        Step 2. Use the MCP Agent tool to retrieve weather data. The data should be formatted in Boolean (True/False) for all relevant days. The returned data should be in JSON, if it isn't, convert it to JSON yourself.

        Step 3. Once the data is collected create a dataframe from the data points using the create dataframe tool. Note that the weather data should NOT have a column for location. Ensure that the dates in both the internal data set and the weather data set match.
        
        The format for weather data input should be:
        {
            {
            "date": "30-11-2025",
            "sunny": True
            },
            {
            "date": "1-12-2025",
            "sunny": False
            }
        }

        Step 4. Return the file path of the CSV generated by create dataframe and the column names for the generated dataset.


        ***CRITICAL***: Do NOT generate any data yourself. Use ONLY the tools provided for data retrieval. If you can't retrieve the data using the tools, inform the user of the issue.
        """

dataframe_agent = create_agent(
    name="dataframe_agent",
    model="openai:gpt-4o-mini",
    tools=[sql_agent_tool, create_dataframe_tool, mcp_agent_tool],
    system_prompt=(DF_SYSTEM_PROMPT
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
        logger.debug("path:", path)  # pragma: no cover
        dataframe = csv_to_pd(path)  # pragma: no cover
        logger.debug("fetched dataframe from csv file:", dataframe)  # pragma: no cover
        return dataframe  # pragma: no cover
    except Exception as e:
        return f"Error fetching dataframe from csv file. {e}"  # pragma: no cover
