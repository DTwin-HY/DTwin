import os

import pandas as pd
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import AgentState
from langchain.messages import HumanMessage, ToolMessage
from langchain.tools import ToolRuntime, tool
from langgraph.types import Command

from ...data_scripts.data_analysis_test_data import create_product_sales_data
from .lin_reg_tool import lin_reg_tool

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


class SimulationState(AgentState):
    dataframe: dict

SIM_AGENT_PROMPT = """
    You are a simulation agent responsible for running company simulations and analyses.

    You have a linear regression tool available for use to conduct analysis. The linear regression tool
    should be used to analyze how different variables affect the variable of interest. The y_value input in the linear regression
    tool should correspond to the variable of interest.

    Return all results as structured JSON.
    """

sim_agent = create_agent(
    model="openai:gpt-4.1",
    tools=[lin_reg_tool],
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
