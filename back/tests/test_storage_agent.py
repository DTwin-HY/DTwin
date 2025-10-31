import pytest
from types import SimpleNamespace
from ..src.services import storage_agent

def test_storage_agent_is_created_correctly(monkeypatch):
    fake_agent = SimpleNamespace(
        name="storage_agent",
        nodes={"tools": SimpleNamespace(bound=SimpleNamespace(tools_by_name={"sql_agent_tool": SimpleNamespace(name="sql_agent_tool")}))}
    )
    monkeypatch.setattr(storage_agent, "storage_react_agent", fake_agent)

    agent = storage_agent.storage_react_agent
    assert agent.name == "storage_agent"
    assert "sql_agent_tool" in agent.nodes["tools"].bound.tools_by_name