import asyncio
import json
import logging
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langchain.tools import tool
from tenacity import retry, wait_fixed, stop_after_attempt
from ..data.mcp_data import WeatherData

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_mcp_agent():
    """
    Create an MCP agent connected to the weather MCP server.
    """
    client = MultiServerMCPClient(
        {
            "weather": {
                "transport": "streamable_http",
                "url": "http://mcp:8000/mcp", # TODO: address from env
            }
        }
    )
    tools = await client.get_tools()
    agent = create_agent(model="openai:gpt-4.1", tools=tools)
    return agent


# Only one valid and complete invoke_mcp_agent function
@retry(wait=wait_fixed(1), stop=stop_after_attempt(3))
async def invoke_mcp_agent(prompt: str) -> str:
    """
    Sends a user query to the MCP agent and returns a WeatherData object.
    Validates and normalizes MCP server response.
    Includes retry logic & error handling.
    """
    agent = await create_mcp_agent()
    payload = {"messages": [{"role": "user", "content": prompt}]}

    try:
        logger.info("Sending prompt to MCP agent: %s", prompt)
        result = await agent.ainvoke(payload)
        logger.debug("Raw MCP result: %s", result)
        return str(result)

        # Validate empty response
        if not result.get("messages"):
            logger.warning("MCP response is empty")
            raise ValueError("MCP response is empty")

        content = result["messages"][-1]["content"]

        data = json.loads(content)
        weather = WeatherData(**data)

        logger.info("MCP data parsed successfully: %s", weather)
        return weather

    except json.JSONDecodeError:
        logger.error("MCP response was not valid JSON")
        raise ValueError("MCP response was not valid JSON")
    except asyncio.TimeoutError:
        logger.error("MCP server timeout")
        raise ValueError("MCP server timeout")
    except Exception as e:
        logger.error("Failed to parse MCP data: %s", e)
        raise ValueError(f"Failed to parse MCP data: {e}")


@tool
def mcp_agent_tool(prompt: str) -> str:
    """
    LangChain tool for invoking the MCP agent.
    Returns the weather information as a JSON string.
    """
    result = asyncio.run(invoke_mcp_agent(prompt))
    logger.info(result)
    return result

    return weather.model_dump_json(indent=2)


if __name__ == "__main__":
    sample = asyncio.run(invoke_mcp_agent("what is the weather like in helsinki?"))
    print(sample.model_dump_json(indent=2))