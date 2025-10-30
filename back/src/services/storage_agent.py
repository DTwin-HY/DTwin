from typing import Annotated

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent
from back.src.services.sql_agent  import sql_agent_tool

load_dotenv()


storage_react_agent = create_react_agent(
    name="storage_agent",
    model="openai:gpt-4o-mini",  # preferably 4o-mini or 5-mini, otherwise queries take too long
    tools=[sql_agent_tool],
    prompt=(
        "You are an **inventory management agent**.\n\n"
        "**Response rules:**\n"
        "- Always respond strictly in JSON format.\n"
        "- No markdown, no natural language text, no explanations.\n"
        '- Example valid response: `{ "A100": 50 }`\n'
        '- If you cannot find data, respond with `{ "error": "reason here" }`.\n'
    ),
)


if __name__ == "__main__":  # pragma: no cover
    for step in storage_react_agent.stream(
        {"messages": [HumanMessage(content="Sum up all the prices in the inventory")]},
        stream_mode="values",
    ):
        print(step["messages"][-1].content)
