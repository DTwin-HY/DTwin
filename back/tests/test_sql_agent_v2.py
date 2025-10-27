from types import SimpleNamespace
import importlib
import os
import pytest

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("OPENAI_API_KEY", "test")

import back.src.services.sql_agent_v2 as sql_agent_v2


def make_msg(content="", tool_calls=None, id="mid"):
    if tool_calls is None:
        tool_calls = []
    return SimpleNamespace(content=content, tool_calls=tool_calls, id=id)


def test_should_continue_no_tool_calls():
    state = {"messages": [make_msg(content="hi", tool_calls=[])]}
    res = sql_agent_v2.should_continue(state)
    assert res == sql_agent_v2.END


def test_should_continue_with_tool_calls():
    state = {"messages": [make_msg(content="hi", tool_calls=[{"foo": "bar"}])]}
    res = sql_agent_v2.should_continue(state)
    assert res == "check_query"


def test_run_sql_agent_invokes_sql_agent(monkeypatch):
    # patch sql_agent.invoke to return a predictable messages list
    fake_invoke = lambda s: {"messages": [make_msg("first"), make_msg("final answer")]}
    monkeypatch.setattr(sql_agent_v2, "sql_agent", SimpleNamespace(invoke=fake_invoke))

    out = sql_agent_v2.run_sql_agent("SELECT 1")
    assert out == "final answer"


def test_list_tables_uses_correct_tool(monkeypatch):
    # Create a fake tool with name and invoke
    def fake_invoke(call):
        # The original code expects an object with .content attribute
        return SimpleNamespace(content="users,orders")

    fake_tool = SimpleNamespace(name="sql_db_list_tables", invoke=fake_invoke)
    monkeypatch.setattr(sql_agent_v2, "tools", [fake_tool])

    res = sql_agent_v2.list_tables({"messages": []})
    assert isinstance(res, dict) and "messages" in res
    msgs = res["messages"]
    assert len(msgs) == 3
    # The last message should include the available tables text
    assert "Available tables" in msgs[-1].content


def test_check_query_sets_response_id(monkeypatch):
    # Create a fake llm.bind_tools that returns an object with invoke
    fake_response = SimpleNamespace(content="checked query", id=None)
    class FakeBound:
        def invoke(self, msgs):
            return fake_response

    def fake_bind_tools(tools, tool_choice=None):
        return FakeBound()

    monkeypatch.setattr(sql_agent_v2, "llm", SimpleNamespace(bind_tools=fake_bind_tools))
    # State where last message has tool_calls and an id
    last_msg = make_msg(content="", tool_calls=[{"args": {"query": "SELECT 1"}}], id="orig-id")
    state = {"messages": [last_msg]}
    out = sql_agent_v2.check_query(state)
    assert out["messages"][0].id == "orig-id"
    assert out["messages"][0].content == "checked query"