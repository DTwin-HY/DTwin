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


sim_agent = create_agent(
    model="openai:gpt-4.1",
    tools=[lin_reg_tool],
    system_prompt=(
        "You are a simulation agent responsible for running company data simulations.\n"
        "You can use the lin_reg_tool to analyze how product sales are affected by "
        "different variables.\n"
        "Return results as structured JSON.\n"
    ),
    state_schema=SimulationState,
    name="simulation_agent",
)


@tool
def simulation_agent_tool(prompt: str) -> str:
    """Run company simulations and analyses using the simulation agent."""
    result = sim_agent.invoke(
        {
            "messages": [HumanMessage(content=prompt)],
        }
    )

    return result["messages"][-1].content
