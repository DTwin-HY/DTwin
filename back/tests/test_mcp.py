import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch, MagicMock
import asyncio

import pytest
import tenacity

from ..src.data.mcp_data import WeatherData
from ..src.services.mcp_client import (
    _extract_weather_data_with_llm,
    create_mcp_agent,
    invoke_mcp_agent,
    _run_in_new_loop,
    mcp_agent_tool,
    WeatherData
)

sys.path.append(str(Path(__file__).resolve().parents[1]))

pytest_plugins = ("pytest_asyncio",)


class DummyClient:
    async def get_tools(self):
        return []


class DummyLLM:
    pass


def dummy_create_agent(*_, **__):
    return SimpleNamespace(dummy="agent")


@pytest.mark.asyncio
async def test_create_mcp_agent_monkeypatched(monkeypatch):
    monkeypatch.setattr(
        "back.src.services.mcp_client.MultiServerMCPClient",
        lambda *a, **k: DummyClient(),
    )
    monkeypatch.setattr("langchain_openai.ChatOpenAI", lambda *a, **k: DummyLLM())
    monkeypatch.setattr("back.src.services.mcp_client.create_agent", dummy_create_agent)

    agent = await create_mcp_agent()
    assert getattr(agent, "dummy", None) == "agent"


@pytest.mark.asyncio
async def test_invoke_mcp_agent():
    test_content = '{"location":"Helsinki","temperature":5,"humidity":80,"condition":"overcast"}'
    fake_agent = SimpleNamespace(
        ainvoke=AsyncMock(return_value=SimpleNamespace(content=test_content))
    )

    with patch("back.src.services.mcp_client.create_mcp_agent", AsyncMock(return_value=fake_agent)):
        test_result = await invoke_mcp_agent("weather in helsinki")

    assert test_result.location == "Helsinki"
    assert test_result.temperature == 5
    assert test_result.humidity == 80
    assert test_result.condition == "overcast"


def test_weatherdata_normalises_fields():
    weather_model = WeatherData(
        city="a", temperature_celsius=0.0, humidity_percent=1.0, description="sunny"
    )
    assert weather_model.location == "a"
    assert weather_model.temperature == 0.0
    assert weather_model.humidity == 1.0
    assert weather_model.condition == "sunny"


@pytest.mark.asyncio
async def test_extract_weather_data_with_llm():
    test_content = '{"location":"Helsinki","temperature":5,"humidity":80,"condition":"overcast"}'
    test_llm = SimpleNamespace(
        ainvoke=AsyncMock(return_value=SimpleNamespace(content=test_content))
    )

    with patch("langchain_openai.ChatOpenAI", lambda *a, **k: test_llm):
        test_result = await _extract_weather_data_with_llm("Narrative", "original prompt")

    assert isinstance(test_result, WeatherData)
    assert test_result.location == "Helsinki"
    assert test_result.temperature == 5
    assert test_result.humidity == 80
    assert test_result.condition == "overcast"


@pytest.mark.asyncio
async def test_invoke_mcp_agent_fallbacks_to_llm_when_no_json(monkeypatch):
    content = "Can't produce JSON for that."
    fake_agent = SimpleNamespace(ainvoke=AsyncMock(return_value=SimpleNamespace(content=content)))
    fallback = WeatherData(location="FallbackCity", temperature=1.0, humidity=10, condition="clear")

    with patch("back.src.services.mcp_client.create_mcp_agent", AsyncMock(return_value=fake_agent)):
        monkeypatch.setattr(
            "back.src.services.mcp_client._extract_weather_data_with_llm",
            AsyncMock(return_value=fallback),
        )
        res = await invoke_mcp_agent("What's the weather for _________")

    assert isinstance(res, WeatherData)
    assert res.location == "FallbackCity"


@pytest.mark.asyncio
async def test_invoke_mcp_agent_agent_raises(monkeypatch):
    fake_agent = AsyncMock()
    fake_agent.ainvoke = AsyncMock(side_effect=RuntimeError())
    monkeypatch.setattr(
        "back.src.services.mcp_client.create_mcp_agent",
        AsyncMock(return_value=fake_agent),
    )
    with pytest.raises(tenacity.RetryError) as excinfo:
        await invoke_mcp_agent("prompt")

    inner = excinfo.value.last_attempt.exception()
    assert isinstance(inner, ValueError)
    assert "Failed to parse MCP data" in str(inner)


def test_run_in_new_loop_executes_coroutine_in_new_loop():
    """Ensure new loop is created, run_until_complete is called, and result is returned."""

    async def fake_coro():
        return "OK"

    # Create a real loop instance so asyncio.set_event_loop accepts it
    real_loop = asyncio.new_event_loop()

    with patch("asyncio.new_event_loop", return_value=real_loop):

        # Patch only the loop methods
        with patch.object(real_loop, "run_until_complete", return_value="OK") as run_mock, \
             patch.object(real_loop, "close") as close_mock:

            result = _run_in_new_loop(fake_coro())

            run_mock.assert_called_once()
            close_mock.assert_called_once()
            assert result == "OK"

    real_loop.close()



def test_mcp_agent_tool_success():
    """mcp_agent_tool returns JSON from WeatherData and calls _run_in_new_loop."""
    weather = WeatherData(
        location="Helsinki", temperature=4, humidity=80, condition="cloudy"
    )

    with patch("back.src.services.mcp_client._run_in_new_loop") as run_mock:
        run_mock.return_value = weather

        # StructuredTool → call via .run()
        result = mcp_agent_tool.run("test")

    run_mock.assert_called_once()
    assert "Helsinki" in result
    assert '"temperature": 4' in result


def test_mcp_agent_tool_error():
    """mcp_agent_tool returns JSON error string when _run_in_new_loop raises."""
    with patch("back.src.services.mcp_client._run_in_new_loop") as run_mock:
        run_mock.side_effect = RuntimeError("boom")

        result = mcp_agent_tool.run("test")

        assert '"error": "boom"' in result

