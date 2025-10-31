<<<<<<< HEAD
import pytest
from langgraph.graph.state import CompiledStateGraph
=======
from types import SimpleNamespace
from ..src.services import storage_agent
>>>>>>> a9b3d44 (Add comments, remove useless imports and fixed)

from ..src.services.storage_agent import storage_react_agent


class TestStorageAgent:
<<<<<<< HEAD
<<<<<<< HEAD
    def test_storage_agent_is_created_correctly(self):
=======
    def test_storage_agent_created_correctly(self):
>>>>>>> 3a3e73e (Add a test for creating the storage agent)
=======
    def test_storage_agent_is_created_correctly(self):
>>>>>>> 67b8848 (Add check for tools)
        test_agent = storage_react_agent

        assert isinstance(test_agent, CompiledStateGraph)

        assert test_agent.name == "storage_agent"
<<<<<<< HEAD
<<<<<<< HEAD
        assert "sql_agent_tool" in test_agent.nodes["tools"].bound.tools_by_name
=======
>>>>>>> 3a3e73e (Add a test for creating the storage agent)
=======
        assert "sql_agent_tool" in test_agent.nodes["tools"].bound.tools_by_name
>>>>>>> 67b8848 (Add check for tools)
