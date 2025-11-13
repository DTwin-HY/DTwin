import asyncio
import json
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langchain.tools import tool
from ..data.mcp_data import WeatherData

load_dotenv()

async def create_mcp_agent():
    """
    Create an MCP agent connected to the weather MCP server.
    """
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


async def invoke_mcp_agent(prompt: str) -> WeatherData:
    """
    Sends a user query to the MCP agent and returns a WeatherData object.
    Validates and normalizes MCP server response.
    """
    agent = await create_mcp_agent()
    payload = {"messages": [{"role": "user", "content": prompt}]}
    result = await agent.ainvoke(payload)

    try:
        content = result["messages"][-1]["content"]
        data = json.loads(content)
        weather = WeatherData(**data)
        return weather

    except json.JSONDecodeError:
        raise ValueError("MCP response was not valid JSON")
    except Exception as e:
        raise ValueError(f"Failed to parse MCP data: {e}")


@tool
def mcp_agent_tool(prompt: str) -> str:
    """
    LangChain tool for invoking the MCP agent.
    Returns the weather information as a JSON string.
    """
    weather = asyncio.run(invoke_mcp_agent(prompt))
    return weather.model_dump_json(indent=2)


if __name__ == "__main__":
    # Quick test run
    sample = asyncio.run(invoke_mcp_agent("what is the weather like in helsinki?"))
    print(sample)