from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langchain.tools import tool
from dotenv import load_dotenv
import asyncio

load_dotenv()


async def create_mcp_agent():
    client = MultiServerMCPClient(
        {
            "weather": {
                "transport": "streamable_http",
                "url": "http://mcp:8000/mcp",
            }
        }
    )
    tools = await client.get_tools()
    agent = create_agent(model="openai:gpt-4.1", tools=tools)
    return agent


async def invoke_mcp_agent(prompt: str) -> str:
    agent = await create_mcp_agent()
    payload = {"messages": [{"role": "user", "content": prompt}]}
    result = await agent.ainvoke(payload)
    try:
        return result["messages"][-1]["content"]
    except Exception:
        return str(result)


@tool
def mcp_agent_tool(prompt: str) -> str:
    """
    Tool for invoking the MCP agent.
    The agent can retrieve weather information from an MCP server.
    Takes a user prompt string and returns the MCP agent's response as a string.
    """
    return asyncio.run(invoke_mcp_agent(prompt))