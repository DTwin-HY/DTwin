import asyncio
import json
import re
import sys
import os
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langchain.tools import tool
from tenacity import retry, wait_fixed, stop_after_attempt
from ..data.mcp_data import WeatherData

# Rich + Loguru logging
from loguru import logger
from rich.logging import RichHandler

load_dotenv()

logger.remove()
# Add RichHandler to stdout
logger.add(
    sys.stdout,
    level="INFO",
    backtrace=True,
    diagnose=True,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | {message}"
)


async def create_mcp_agent():
    """Create MCP agent connected to weather server."""
    from langchain_openai import ChatOpenAI
    
    client = MultiServerMCPClient(
        {
            "weather": {
                "transport": "streamable_http",
                "url": os.getenv("WEATHER_MCP_URL", "http://mcp:8000/mcp"),
            }
        }
    )
    tools = await client.get_tools()
    llm = ChatOpenAI(model="gpt-4-turbo-preview")
    agent = create_agent(model=llm, tools=tools)
    return agent


async def _extract_weather_data_with_llm(narrative_text: str, original_prompt: str) -> WeatherData:
    """Parse narrative weather response into structured WeatherData using LLM."""
    from langchain_openai import ChatOpenAI
    
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        model_kwargs={"response_format": {"type": "json_object"}}
    )
    
    extraction_prompt = f"""Extract weather information from the following text and return ONLY a JSON object.

Original query: {original_prompt}

Weather report:
{narrative_text}

Return a JSON object with these fields:
- location: string (city name)
- temperature: number (average or representative temperature in Celsius)
- humidity: number or null (if mentioned)
- condition: string or null (brief weather description like "overcast", "clear", "snowy")

JSON object:"""
    
    response = await llm.ainvoke(extraction_prompt)
    response_text = response.content
    response_text = re.sub(r'```json\s*|\s*```', '', response_text).strip()
    data = json.loads(response_text)
    return WeatherData(**data)


async def invoke_mcp_agent(prompt: str) -> WeatherData:
    """
    Send query to MCP agent and return structured WeatherData.
    Retries up to 3 times on failure.
    """
    agent = await create_mcp_agent()
    payload = {"messages": [{"role": "user", "content": prompt}]}

    try:
        logger.info("Sending prompt to MCP agent: {}", prompt)
        result = await agent.ainvoke(payload)
        logger.debug("Raw MCP result: {}", result)
        
        result_text = str(result)
        logger.debug("Result text: {}", result_text)
        
        # Try to extract JSON directly from response
        json_matches = re.finditer(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', result_text, re.DOTALL)
        
        for json_match in json_matches:
            try:
                json_str = json_match.group(0)
                data = json.loads(json_str)
                
                # Skip incomplete objects
                if not data or 'location' not in data or 'temperature' not in data:
                    logger.debug("Skipping incomplete JSON: {}", json_str)
                    continue
                
                weather_data = WeatherData(**data)
                logger.info("Successfully parsed WeatherData from JSON: {}", weather_data)
                return weather_data
            except (json.JSONDecodeError, Exception) as e:
                logger.debug("Failed to parse JSON candidate: {}", e)
                continue
        
        # Fallback: extract structured data using LLM
        logger.info("No valid JSON found, extracting data with LLM...")
        weather_data = await _extract_weather_data_with_llm(result_text, prompt)
        logger.info("Successfully extracted WeatherData with LLM: {}", weather_data)
        return weather_data

    except asyncio.TimeoutError:
        logger.error("MCP server timeout")
        raise ValueError("MCP server timeout")
    except Exception as e:
        logger.error("Failed to parse MCP data: {}", e)
        raise ValueError(f"Failed to parse MCP data: {e}")


@tool
def mcp_agent_tool(prompt: str) -> str:
    """LangChain tool wrapper for MCP agent. Returns weather data as JSON string."""
    try:
        result = asyncio.run(invoke_mcp_agent(prompt))
        logger.info("MCP agent result: {}", result)
        return result.model_dump_json(indent=2)
    except Exception as e:
        logger.error("Error in mcp_agent_tool: {}", e)
        return json.dumps({"error": str(e)})


if __name__ == "__main__":
    sample = asyncio.run(invoke_mcp_agent("what is the weather like in helsinki?"))
    print(sample.model_dump_json(indent=2))
