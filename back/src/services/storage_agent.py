from dotenv import load_dotenv
from langchain.messages import HumanMessage
from langchain.agents import create_agent
from langchain.tools import tool

from .sql_agent import sql_agent_tool

load_dotenv()


storage_react_agent = create_agent(
    name="storage_agent",
    model="openai:gpt-4o-mini",  # preferably 4o-mini or 5-mini, otherwise queries take too long
    tools=[sql_agent_tool],
    system_prompt=(
        "You are an **inventory management agent**.\n\n"
        "**Response rules:**\n"
        "- Always respond strictly in JSON format.\n"
        "- No markdown, no natural language text, no explanations.\n"
        '- Example valid response: `{ "A100": 50 }`\n'
        '- If you cannot find data, respond with `{ "error": "reason here" }`.\n'
    ),
)

@tool
def storage_agent_tool(prompt: str) -> str:
    """
    Wraps the storage_react_agent as a tool.
    Takes a user prompt string and returns the agent's response as a string.
    """
    result = storage_react_agent.invoke({"messages": [HumanMessage(content=prompt)]})
    return result["messages"][-1].content

if __name__ == "__main__":  # pragma: no cover
    for step in storage_react_agent.stream(
        {"messages": [HumanMessage(content="Sum up all the prices in the inventory")]},
        stream_mode="values",
    ):
        print(step["messages"][-1].content)
