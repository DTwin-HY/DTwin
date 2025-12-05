# pylint: skip-file
import asyncio
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_mcp_adapters.client import MultiServerMCPClient
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_fixed

from ..data.mcp_data import WeatherData
from ..utils.logger import logger

load_dotenv()


def _run_in_new_loop(coroutine):
    """Run a coroutine in a new event loop in a thread pool."""
    executor = ThreadPoolExecutor(max_workers=4)

    def run():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coroutine)
        finally:
            loop.close()

    return executor.submit(run).result()


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


def extract_json_from_mcp(result):
    """
    Extract a textual payload from the MCP result,
    handling JSON-RPC wrappers and tool metadata.
    Returns empty string when the result is tools/metadata
    or contains no user-facing text.
    """
    if isinstance(result, str):
        s = result.strip()
        if s.startswith("{") or s.startswith("["):
            return s

    content = getattr(result, "content", None)
    if isinstance(content, str):
        s = content.strip()
        if s.startswith("{") or s.startswith("["):
            return s

    if isinstance(result, dict) and "messages" in result:
        for msg in reversed(result["messages"]):
            c = getattr(msg, "content", None)
            if isinstance(c, str):
                s = c.strip()
                if s.startswith("{") or s.startswith("["):
                    return s

    if isinstance(result, dict):
        for key in ("content", "output", "response", "result"):
            val = result.get(key)
            if isinstance(val, str):
                s = val.strip()
                if s.startswith("{") or s.startswith("["):
                    return s

    return None


@retry(wait=wait_fixed(1), stop=stop_after_attempt(3))
async def invoke_mcp_agent(prompt: str):
    agent = await create_mcp_agent()

    prompt = f"""{prompt}

IMPORTANT:
Return ONLY valid JSON.
NO markdown code fences.
Format each weather entry exactly like this:

{{
  "date": "dd-mm-yyyy",
  "location": "city name",
  "sunny": true/false
}}

If multiple results exist, return a JSON array of objects.
"""

    payload = {"messages": [{"role": "user", "content": prompt}]}

    try:
        logger.info("Sending prompt to MCP agent: {}", prompt)
        result = await agent.ainvoke(payload)

        logger.info("Received MCP raw result type={}", type(result))
        logger.info("Received MCP raw result (full): {}", repr(result)[:1000])

        result_text = extract_json_from_mcp(result)
        if not result_text:
            logger.warning("No usable JSON extracted from MCP result")
            return {"error": "Empty response", "raw_result": str(result)[:500]}

        result_text = result_text.strip()
        logger.info("Extracted text: {}", result_text[:500])

        if result_text.startswith("```"):
            lines = result_text.splitlines()
            if lines[0].startswith("```") and lines[-1].startswith("```"):
                result_text = "\n".join(lines[1:-1]).strip()

        try:
            parsed = json.loads(result_text)
            logger.info("Parsed JSON successfully: {}", type(parsed))
        except json.JSONDecodeError as e:
            logger.error("JSON decode failed: {}", e)
            return {
                "error": "Could not parse JSON",
                "raw_text": result_text[:500],
                "exception": str(e),
            }

        if isinstance(parsed, list):
            validated = []
            for item in parsed:
                try:
                    weather_data = WeatherData.model_validate(item)
                    validated.append(weather_data)
                except Exception:
                    try:
                        normalized = _normalize_weather_item(item)
                        validated.append(WeatherData.model_validate(normalized))
                    except Exception as err:
                        validated.append({"error": str(err), "original": item})

            return validated

        if isinstance(parsed, dict):
            try:
                return WeatherData.model_validate(parsed)
            except Exception:
                try:
                    normalized = _normalize_weather_item(parsed)
                    return WeatherData.model_validate(normalized)
                except Exception as err:
                    return {"error": str(err), "original": parsed}

        return parsed

    except asyncio.TimeoutError:
        raise ValueError("MCP server timeout")
    except Exception as e:
        logger.exception("Failed to parse MCP data: {}", e)
        return {"error": str(e), "type": type(e).__name__}


def _normalize_weather_item(item: dict) -> dict:
    """
    Normalize a dict to match WeatherData schema.
    Handles common field name variations.
    """
    normalized = {}

    logger.debug(f"Normalizing item with keys: {list(item.keys())}")

    if "location" in item:
        normalized["location"] = str(item["location"])
    elif "city" in item:
        normalized["location"] = str(item["city"])
    elif "place" in item:
        normalized["location"] = str(item["place"])
    else:
        logger.warning("No location field found, using 'Unknown'")
        normalized["location"] = "Unknown"

    if "date" in item:
        normalized["date"] = str(item["date"])
    elif "datetime" in item:
        normalized["date"] = str(item["datetime"])
    elif "time" in item:
        normalized["date"] = str(item["time"])
    else:
        logger.warning("No date field found, using current date")
        from datetime import datetime

        normalized["date"] = datetime.now().strftime("%d-%m-%Y")

    if "sunny" in item:
        sunny_val = item["sunny"]
        if isinstance(sunny_val, bool):
            normalized["sunny"] = sunny_val
        elif isinstance(sunny_val, str):
            normalized["sunny"] = sunny_val.lower() in ("true", "1", "yes", "sunny")
        else:
            normalized["sunny"] = bool(sunny_val)
    else:
        logger.warning("No sunny field found, defaulting to False")
        normalized["sunny"] = False

    logger.debug(f"Normalized result: {normalized}")
    return normalized


@tool
def mcp_agent_tool(prompt: str) -> str:
    """LangChain tool wrapper for MCP agent.
    Returns weather data as JSON string in WeatherData format."""
    try:
        result = _run_in_new_loop(invoke_mcp_agent(prompt))
        logger.info("MCP agent result type={}", type(result))
        logger.info("MCP agent result content={}", repr(result)[:500])

        if isinstance(result, dict) and "error" in result:
            logger.error(f"MCP agent returned error: {result}")
            return json.dumps(result, indent=2, ensure_ascii=False)

        if isinstance(result, list):  # pragma: no cover
            serialized = []
            for item in result:
                try:
                    # pydantic model
                    if hasattr(item, "model_dump"):
                        serialized.append(item.model_dump())
                    else:
                        serialized.append(item)
                except Exception as e:
                    logger.warning(f"Error serializing item: {e}")
                    serialized.append(item)
            return json.dumps(serialized, indent=2, ensure_ascii=False)

        if hasattr(result, "model_dump_json"):  # pragma: no cover
            try:
                return result.model_dump_json(indent=2)
            except Exception:
                pass
        if hasattr(result, "model_dump"):  # pragma: no cover
            try:
                return json.dumps(result.model_dump(), indent=2, ensure_ascii=False)
            except Exception:
                pass

        return json.dumps(result, indent=2, ensure_ascii=False, default=str)
    except Exception as e:
        logger.exception("Error in mcp_agent_tool: {}", e)
        return json.dumps({"error": str(e), "error_type": type(e).__name__})
