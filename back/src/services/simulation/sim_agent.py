import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langchain_core.tools import StructuredTool

from langchain.tools import tool, ToolRuntime
from langchain.agents.middleware import AgentState
import pandas as pd

from .lin_reg_tool import lin_reg_tool
from ...data_scripts.data_analysis_test_data import create_product_sales_data



load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

class SimulationState(AgentState):
    df: dict #State does not allow pd dataframes



sim_agent = create_agent(
    model="openai:gpt-4.1",
    tools=[lin_reg_tool],
    system_prompt=(
        "You are a simulation agent responsible for running company data simulations.\n"
        "You can use the lin_reg_tool to analyze how product sales are affected by different variables.\n"
        "Return results as structured JSON.\n"
    ),
    state_schema=SimulationState,
    name="simulation_agent",
)

###Structured tool version
#def run_sim_agent(prompt: str,) -> str:
#    result = sim_agent.invoke({"messages": [HumanMessage(content=prompt)]})
#    return result["messages"][-1].content
#
#simulation_agent_tool = StructuredTool.from_function(
#    func=run_sim_agent,
#    name="simulation_agent",
#    description="Run company simulations and analyses using the simulation agent.",
#)
###

###@tool wrapper version

@tool
def simulation_agent_tool(prompt:str) -> str:
    """Run company simulations and analyses using the simulation agent."""
    result = sim_agent.invoke({"messages": [HumanMessage(content=prompt)],})

    return result["messages"][-1].content
###


if __name__ == "__main__":

    df = create_product_sales_data()
    data = df.to_dict(orient="records")

    #print(data)

    user_message = (
        "Run a linear regression simulation on the following dataset."
        "and explain the coefficients:\n\n"
        f"{data}\n"
        "You can do any required modifications to the data."
    )

    response = sim_agent.invoke({"messages": [{"role": "user", "content": user_message}],})

    print(response["messages"][-1].content)
