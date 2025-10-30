import pytest
from langgraph.graph.state import CompiledStateGraph

from ..src.services.storage_agent import storage_react_agent


class TestStorageAgent:
    def test_storage_agent_is_created_correctly(self):
        test_agent = storage_react_agent

        assert isinstance(test_agent, CompiledStateGraph)

        assert test_agent.name == "storage_agent"
        assert "sql_agent_tool" in test_agent.nodes["tools"].bound.tools_by_name
