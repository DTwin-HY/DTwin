import os

import pandas as pd
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import AgentState
from langchain.messages import HumanMessage, ToolMessage
from langchain.tools import ToolRuntime, tool
from langgraph.types import Command

from ...data_scripts.data_analysis_test_data import create_product_sales_data
from ..dataframe_creation import csv_dataframe_test_tool, dataframe_agent_tool
from .lin_reg_tool import lin_reg_tool

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


class SimulationState(AgentState):
    dataframe: dict

SIM_AGENT_PROMPT = """
    You are an analytics agent responsible for running company simulations and analyses.

    You have the following tools available:

        1. Linear regression tool: used to do statistical analysis on how variables interact. The y_value input in the linear regression
        tool should correspond to the variable of interest in the query.

        2. The dataframe creation tool: used to collate a dataset that can be used in the linear regression tool. Once the data is collected,
        the dataframe agent will return a file path for the dataset. This is string must be passed to the linear regression tool along with 
        the y_value.
    

    Example task (Statistical analysis/linear regression workflow):

    Incoming prompt: Analyze the effect of sunny weather, customer amounts and prices on total sales for the period 25.11-30.11.2025.

    Step 1: Instruct the dataframe collection tool to collate a dataset with relevant datapoints on sunny weather, customer amounts, prices and total sales for the time period.

    Step 2: Pass the file path from the dataframe tool and the y_value, which should be the variable of interest so in this case, total sales, to the linear regression tool.

    Step 3: Return the results of your analysis to the prompter.

    Return all results as structured JSON.
    """

sim_agent = create_agent(
    model="openai:gpt-4.1",
    tools=[lin_reg_tool, dataframe_agent_tool],
    system_prompt= SIM_AGENT_PROMPT,
    state_schema=SimulationState,
    name="analytics_agent",
)


@tool
def analytics_agent_tool(prompt: str) -> str:
    """Run company simulations and analyses using the analytics agent."""
    result = sim_agent.invoke(
        {
            "messages": [HumanMessage(content=prompt)],
        }
    )

    return result["messages"][-1].content
