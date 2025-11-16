import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.messages import HumanMessage, ToolMessage
from langchain_core.tools import StructuredTool
from langgraph.types import Command

from langchain.tools import tool, ToolRuntime
from langchain.agents.middleware import AgentState
import pandas as pd

from .lin_reg_tool import lin_reg_tool
from ...data_scripts.data_analysis_test_data import create_product_sales_data



load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class SimulationState(AgentState):
    dataframe: dict 

### TODO: Temp data fetch for branch testing. DROP BEFORE MERGE!
@tool
def fetch_data_tool(prompt: str, runtime: ToolRuntime) -> Command:
    """
    Fetches data for a linear regression and writes it to file.
    Returns the file location which can be passed to the linear regression.
    """

    df = create_product_sales_data()
    if not os.path.exists("dataframes"):
        os.makedirs("dataframes")
    file_path = f"dataframes/csv_data.csv"
    df.to_csv(file_path, index=False)

    print(f"[create_array_tool_file] DataFrame saved to {file_path}, shape {df.shape}")


    return Command(update={
        "messages": [
            ToolMessage(
                content=f"Pd dataframe saved to file: {file_path}",
                tool_call_id=runtime.tool_call_id
            )
        ]
    })
#####

sim_agent = create_agent(
    model="openai:gpt-4.1",
    tools=[lin_reg_tool, fetch_data_tool], # TODO: Remove fetch_data tool before merge
    system_prompt=(
        "You are a simulation agent responsible for running company data simulations.\n"
        "You can use the lin_reg_tool to analyze how product sales are affected by different variables.\n"
        "Return results as structured JSON.\n"
    ),
    state_schema=SimulationState,
    name="simulation_agent",
)

@tool
def simulation_agent_tool(prompt:str) -> str:
    """Run company simulations and analyses using the simulation agent."""
    result = sim_agent.invoke({"messages": [HumanMessage(content=prompt)],})

    return result["messages"][-1].content
