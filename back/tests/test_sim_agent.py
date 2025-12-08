from unittest.mock import MagicMock, patch

from langchain.messages import HumanMessage

from ..src.services.simulation import analytics_agent as analytics_module


def test_analytics_agent_tool_invoke_works_with_tool_wrapper(monkeypatch):
    prompt = "Run a linear regression simulation"

    fake_result = {"messages": [HumanMessage(content=prompt), HumanMessage(content="final reply")]}

    fake_agent = MagicMock()
    fake_agent.invoke.return_value = fake_result
    monkeypatch.setattr(analytics_module, "sim_agent", fake_agent)
    result = analytics_module.analytics_agent_tool.invoke({"prompt": prompt})

    fake_agent.invoke.assert_called_once()
    args_passed = fake_agent.invoke.call_args.args[0]
    assert "messages" in args_passed
    assert args_passed["messages"][0].content == prompt

    assert result == "final reply"
