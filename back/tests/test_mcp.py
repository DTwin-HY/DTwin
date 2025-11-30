import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from ..src.data.mcp_data import WeatherData
from ..src.services.mcp_client import (
    _normalize_weather_item,
    _run_in_new_loop,
    create_mcp_agent,
    extract_json_from_mcp,
    invoke_mcp_agent,
    mcp_agent_tool,
)

sys.path.append(str(Path(__file__).resolve().parents[1]))

pytest_plugins = ("pytest_asyncio",)


class DummyClient:
    async def get_tools(self):
        return []


class DummyLLM:
    pass


class Msg:
    def __init__(self, content):
        self.content = content


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
    test_content = '{"date":"01-01-1960","location":"Helsinki","sunny": false}'

    fake_agent = SimpleNamespace(
        ainvoke=AsyncMock(return_value=SimpleNamespace(content=test_content))
    )

    with patch("back.src.services.mcp_client.create_mcp_agent", AsyncMock(return_value=fake_agent)):
        test_result = await invoke_mcp_agent("weather in helsinki")

    assert test_result.location == "Helsinki"
    assert test_result.date == "01-01-1960"
    assert test_result.sunny is False


@pytest.mark.asyncio
async def test_invoke_mcp_agent_invalid_content():
    test_content = '{"invalid"}'

    fake_agent = SimpleNamespace(
        ainvoke=AsyncMock(return_value=SimpleNamespace(content=test_content))
    )

    with patch("back.src.services.mcp_client.create_mcp_agent", AsyncMock(return_value=fake_agent)):
        test_result = await invoke_mcp_agent("weather in helsinki")

    assert "error" in test_result


@pytest.mark.asyncio
async def test_invoke_mcp_agent_invalid_json():
    test_content = "---"

    fake_agent = SimpleNamespace(
        ainvoke=AsyncMock(return_value=SimpleNamespace(content=test_content))
    )

    with patch("back.src.services.mcp_client.create_mcp_agent", AsyncMock(return_value=fake_agent)):
        test_result = await invoke_mcp_agent("weather in helsinki")

    assert "error" in test_result


@pytest.mark.asyncio
async def test_invoke_mcp_agent_code_block():
    test_content = '{"date":"01-01-1960","location":"Helsinki","sunny": false}'

    fake_agent = SimpleNamespace(
        ainvoke=AsyncMock(return_value=SimpleNamespace(content=test_content))
    )

    with patch("back.src.services.mcp_client.create_mcp_agent", AsyncMock(return_value=fake_agent)):
        with patch(
            "back.src.services.mcp_client.extract_json_from_mcp",
            MagicMock(
                return_value='```{"date":"01-01-1960","location":"Helsinki","sunny": false}```'
            ),
        ):
            test_result = await invoke_mcp_agent("weather in helsinki")

    assert "error" in test_result


def test_weatherdata_normalises_fields():
    weather_model = WeatherData(city="a", date="26-11-2025", sunny="Yes")
    assert weather_model.location == "a"
    assert weather_model.date == "26-11-2025"
    assert weather_model.sunny is True


def test_normalize_weather_item():
    item = {"location": "Helsinki", "date": "01-01-1999", "sunny": "true"}
    desired = {"location": "Helsinki", "date": "01-01-1999", "sunny": True}
    assert _normalize_weather_item(item) == desired


def test_normalize_weather_item_location_normalized():
    item1 = {"city": "Helsinki", "date": "01-01-1999", "sunny": "true"}
    desired1 = {"location": "Helsinki", "date": "01-01-1999", "sunny": True}
    item2 = {"place": "Helsinki", "date": "01-01-1999", "sunny": "true"}
    desired2 = {"location": "Helsinki", "date": "01-01-1999", "sunny": True}
    item3 = {"date": "01-01-1999", "sunny": "true"}
    desired3 = {"location": "Unknown", "date": "01-01-1999", "sunny": True}
    assert _normalize_weather_item(item1) == desired1
    assert _normalize_weather_item(item2) == desired2
    assert _normalize_weather_item(item3) == desired3


def test_normalize_weather_item_date_normalized():
    item1 = {"city": "Helsinki", "time": "01-01-1999", "sunny": "true"}
    desired1 = {"location": "Helsinki", "date": "01-01-1999", "sunny": True}
    item2 = {"place": "Helsinki", "datetime": "01-01-1999", "sunny": "true"}
    desired2 = {"location": "Helsinki", "date": "01-01-1999", "sunny": True}
    item3 = {"location": "Helsinki", "sunny": "true"}
    desired3 = {"location": "Helsinki", "date": datetime.now().strftime("%d-%m-%Y"), "sunny": True}
    assert _normalize_weather_item(item1) == desired1
    assert _normalize_weather_item(item2) == desired2
    assert _normalize_weather_item(item3) == desired3


def test_normalize_weather_item_sunny_normalized():
    item1 = {"city": "Helsinki", "time": "01-01-1999", "sunny": True}
    desired1 = {"location": "Helsinki", "date": "01-01-1999", "sunny": True}
    item2 = {"city": "Helsinki", "time": "01-01-1999", "sunny": "true"}
    desired2 = {"location": "Helsinki", "date": "01-01-1999", "sunny": True}
    item3 = {"city": "Helsinki", "time": "01-01-1999", "sunny": 1}
    desired3 = {"location": "Helsinki", "date": "01-01-1999", "sunny": True}
    item4 = {"city": "Helsinki", "time": "01-01-1999"}
    desired4 = {"location": "Helsinki", "date": "01-01-1999", "sunny": False}
    assert _normalize_weather_item(item1) == desired1
    assert _normalize_weather_item(item2) == desired2
    assert _normalize_weather_item(item3) == desired3
    assert _normalize_weather_item(item4) == desired4


def test_extract_json_from_mcp_brackets():
    mcp_result = "[test]"
    assert extract_json_from_mcp(mcp_result) == mcp_result


def test_extract_json_from_mcp_dict():
    mcp_result = {"messages": [Msg("[test]")]}
    assert extract_json_from_mcp(mcp_result) == "[test]"


def test_extract_json_from_content_key():
    mcp_result = {"content": "[test]"}
    assert extract_json_from_mcp(mcp_result) == "[test]"


def test_extract_json_none():
    mcp_result = {"content": ""}
    assert extract_json_from_mcp(mcp_result) is None


def test_run_in_new_loop_executes_coroutine_in_new_loop():
    """Ensure new loop is created, run_until_complete is called, and result is returned."""

    async def fake_coro():
        return "OK"

    # Create a real loop instance so asyncio.set_event_loop accepts it
    real_loop = asyncio.new_event_loop()

    with patch("asyncio.new_event_loop", return_value=real_loop):

        # Patch only the loop methods
        with (
            patch.object(real_loop, "run_until_complete", return_value="OK") as run_mock,
            patch.object(real_loop, "close") as close_mock,
        ):

            result = _run_in_new_loop(fake_coro())

            run_mock.assert_called_once()
            close_mock.assert_called_once()
            assert result == "OK"

    real_loop.close()


def test_mcp_agent_tool_success():
    """mcp_agent_tool returns JSON from WeatherData and calls _run_in_new_loop."""
    weather = WeatherData(date="25-11-2025", location="Helsinki", sunny=False)

    with patch("back.src.services.mcp_client._run_in_new_loop") as run_mock:
        run_mock.return_value = weather

        # StructuredTool → call via .run()
        result = mcp_agent_tool.run("test")

    run_mock.assert_called_once()
    assert "Helsinki" in result
    assert '"sunny": false' in result


def test_mcp_agent_tool_error():
    """mcp_agent_tool returns JSON error string when _run_in_new_loop raises."""
    with patch("back.src.services.mcp_client._run_in_new_loop") as run_mock:
        run_mock.side_effect = RuntimeError()

        result = mcp_agent_tool.run("test")

        assert "error" in result


@pytest.mark.asyncio
async def test_invoke_mcp_agent_agent_raises_returns_error_dict():
    fake_agent = SimpleNamespace(ainvoke=AsyncMock(side_effect=RuntimeError("agent-failed")))
    with patch("back.src.services.mcp_client.create_mcp_agent", AsyncMock(return_value=fake_agent)):
        res = await invoke_mcp_agent("weather in helsinki")
    assert isinstance(res, dict)
    assert "error" in res
    assert "agent-failed" in res["error"] or res.get("type") == "RuntimeError"


@pytest.mark.asyncio
async def test_invoke_mcp_agent_list_response_validates_items():
    arr = [
        {"date": "01-01-1960", "location": "Helsinki", "sunny": False},
        {"city": "Turku", "time": "02-02-2000", "sunny": "true"},
    ]
    fake_agent = SimpleNamespace(
        ainvoke=AsyncMock(return_value=SimpleNamespace(content=json.dumps(arr)))
    )
    with patch("back.src.services.mcp_client.create_mcp_agent", AsyncMock(return_value=fake_agent)):
        res = await invoke_mcp_agent("weather in finland")
    assert isinstance(res, list)
    validated = []
    for item in res:
        if isinstance(item, dict):
            validated.append(WeatherData.model_validate(item))
        else:
            validated.append(item)
    assert validated[0].location == "Helsinki"
    assert validated[1].location == "Turku"


@pytest.mark.asyncio
async def test_invoke_mcp_agent_extract_none_returns_empty_error():
    """If extract_json_from_mcp yields no usable text, function returns Empty response error."""
    fake_agent = SimpleNamespace(
        ainvoke=AsyncMock(return_value=SimpleNamespace(content="irrelevant"))
    )
    with (
        patch("back.src.services.mcp_client.create_mcp_agent", AsyncMock(return_value=fake_agent)),
        patch("back.src.services.mcp_client.extract_json_from_mcp", return_value=None),
    ):
        res = await invoke_mcp_agent("weather in helsinki")
    assert isinstance(res, dict)
    assert res.get("error") == "Empty response"


@pytest.mark.asyncio
async def test_invoke_mcp_agent_normalize_dict_then_validate():
    """If MCP returns a dict with alternate keys, _normalize_weather_item should be applied and validated."""
    payload = {"city": "Oulu", "datetime": "03-03-2003", "sunny": "true"}
    fake_agent = SimpleNamespace(
        ainvoke=AsyncMock(return_value=SimpleNamespace(content=json.dumps(payload)))
    )
    with patch("back.src.services.mcp_client.create_mcp_agent", AsyncMock(return_value=fake_agent)):
        res = await invoke_mcp_agent("weather in oulu")
    if isinstance(res, dict) and "error" in res:
        pytest.fail(f"Expected validated WeatherData, got error: {res}")
    if isinstance(res, dict):
        res = WeatherData.model_validate(res)
    assert res.location == "Oulu"
    assert res.date.replace("/", "-")
