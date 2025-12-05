from unittest.mock import MagicMock, patch

from langchain.messages import HumanMessage

from ..src.services.simulation import sim_agent as sim_module


def test_simulation_agent_tool_invoke_works_with_tool_wrapper(monkeypatch):
    prompt = "Run a linear regression simulation"

    fake_result = {"messages": [HumanMessage(content=prompt), HumanMessage(content="final reply")]}

    fake_agent = MagicMock()
    fake_agent.invoke.return_value = fake_result
    monkeypatch.setattr(sim_module, "sim_agent", fake_agent)
    result = sim_module.simulation_agent_tool.invoke({"prompt": prompt})

    fake_agent.invoke.assert_called_once()
    args_passed = fake_agent.invoke.call_args.args[0]
    assert "messages" in args_passed
    assert args_passed["messages"][0].content == prompt

    assert result == "final reply"
