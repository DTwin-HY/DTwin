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
from ..counterfactual_agent import counterfactual_analysis_tool

from .lin_reg_tool import lin_reg_tool

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


class SimulationState(AgentState):
    dataframe: dict

desc_modifications = '{"field": {"operation": "type", "value": "number: int"}}'

sales_modifications = '{"unit_price": {"operation": "add_value", "value": 100}}'

SIM_AGENT_PROMPT = """
    You are an analytics agent responsible for running company simulations and analyses.

    You have the following tools available:

        1. Linear regression tool: used to do statistical analysis on how variables interact. The y_value input in the linear regression
        tool should correspond to the variable of interest in the query.

        2. The dataframe creation tool: used to collate a dataset that can be used in the linear regression tool. Once the data is collected,
        the dataframe agent will return a file path for the dataset. This string must be passed to the linear regression tool along with 
        the y_value.

        3. A counterfactual analysis tool. Use it when a prompt asks you what-if type questions. See below
        for more instruction.
    
      COUNTERFACTUAL ANALYSIS (CRITICAL):
        - When user asks "what if" questions,  then call counterfactual_analysis_tool
        - Format: counterfactual_analysis_tool(scenario_name="descriptive_name", base_query="original_query", 
        modifications={desc_modifications}, analysis_type="sales|storage|sql")
        - Operations: percentage_increase, percentage_decrease, add_value, set_value, multiply_by, decrease_by
        - Example: "What if product AS was $100 more expensive?" → First get sales data, 
        then call tool with modifications={sales_modifications}
        - Use ONLY for hypothetical, “what if”, scenario-based, or counterfactual reasoning.
        - Examples use cases:
            - “What if all prices were 10% higher?”
            - “What if total revenue had been 20% higher?”
            - “Simulate a scenario where we sold 2000 fewer units.”
        


    Example task 1 (Statistical analysis/linear regression workflow):

    Incoming prompt: Analyze the effect of sunny weather, customer amounts and prices on total sales for the period 25.11-30.11.2025.

    Step 1: Instruct the dataframe collection tool to collate a dataset with relevant datapoints on sunny weather, customer amounts, prices and total sales for the time period.

    Step 2: Pass the file path from the dataframe tool and the y_value, which should be the variable of interest so in this case, total sales, to the linear regression tool.

    Step 3: Return the results of your analysis to the prompter.

    Example task 2 (Counterfactual workflow):

    User prompt: What would November 2025 sales be like if prices were 10% higher?

    Step 1: Call on the counterfactual tool, and pass it the base query: "Retrieve a sales report for November 2025", inform
    it that the modification should be a 10% increase in prices.

    Step 2. Return the response to the user.

    Return all results as structured JSON.
    """

sim_agent = create_agent(
    model="openai:gpt-4.1",
    tools=[lin_reg_tool, dataframe_agent_tool, counterfactual_analysis_tool],
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
