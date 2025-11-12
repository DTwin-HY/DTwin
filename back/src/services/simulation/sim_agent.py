import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.messages import HumanMessage
from langchain_core.tools import StructuredTool

from src.services.simulation.lin_reg_tool import lin_req_tool

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


sim_agent = create_agent(
    model="openai:gpt-4.1",
    tools=[lin_req_tool],
    system_prompt=(
        "You are a simulation agent responsible for running company data simulations.\n"
        "You can use the lin_req_tool to analyze how product sales are affected by different variables.\n"
        "Return results as structured JSON.\n"
    ),
    name="simulation_agent",
)


def run_sim_agent(prompt: str) -> str:
    result = sim_agent.invoke({"messages": [HumanMessage(content=prompt)]})
    return result["messages"][-1].content


simulation_agent_tool = StructuredTool.from_function(
    func=run_sim_agent,
    name="simulation_agent",
    description="Run company simulations and analyses using the simulation agent.",
)


if __name__ == "__main__":
    from src.data.data_analysis_test_data import create_product_sales_data

    df = create_product_sales_data()
    data = df.to_dict(orient="records")

    print(data)

    user_message = (
        "Run a linear regression simulation on the following dataset."
        "and explain the coefficients:\n\n"
        f"{data}"
    )

    response = sim_agent.invoke({"messages": [{"role": "user", "content": user_message}]})

    print(response["messages"][-1].content)
