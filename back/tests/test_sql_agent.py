from types import SimpleNamespace
import importlib
import os
import pytest

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("OPENAI_API_KEY", "test")

import back.src.services.sql_agent as sql_agent


def make_msg(content="", tool_calls=None, id="mid"):
    if tool_calls is None:
        tool_calls = []
    return SimpleNamespace(content=content, tool_calls=tool_calls, id=id)


def test_should_continue_no_tool_calls():
    state = {"messages": [make_msg(content="hi", tool_calls=[])]}
    res = sql_agent.should_continue(state)
    assert res == sql_agent.END


def test_should_continue_with_tool_calls():
    state = {"messages": [make_msg(content="hi", tool_calls=[{"foo": "bar"}])]}
    res = sql_agent.should_continue(state)
    assert res == "check_query"


def test_run_sql_agent_invokes_sql_agent(monkeypatch):
    # patch sql_agent.invoke to return a predictable messages list
    fake_invoke = lambda s: {"messages": [make_msg("first"), make_msg("final answer")]}
    monkeypatch.setattr(sql_agent, "sql_agent", SimpleNamespace(invoke=fake_invoke))

    out = sql_agent.run_sql_agent("SELECT 1")
    assert out == "final answer"


def test_list_tables_uses_correct_tool(monkeypatch):
    # Create a fake tool with name and invoke
    def fake_invoke(call):
        # The original code expects an object with .content attribute
        return SimpleNamespace(content="users,orders")

    fake_tool = SimpleNamespace(name="sql_db_list_tables", invoke=fake_invoke)
    monkeypatch.setattr(sql_agent, "tools", [fake_tool])

    res = sql_agent.list_tables({"messages": []})
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

    monkeypatch.setattr(sql_agent, "llm", SimpleNamespace(bind_tools=fake_bind_tools))
    # State where last message has tool_calls and an id
    last_msg = make_msg(content="", tool_calls=[{"args": {"query": "SELECT 1"}}], id="orig-id")
    state = {"messages": [last_msg]}
    out = sql_agent.check_query(state)
    assert out["messages"][0].id == "orig-id"
    assert out["messages"][0].content == "checked query"


def test_generate_query_invokes_llm(monkeypatch):
    # fake response object the bound LLM will return
    fake_response = SimpleNamespace(content="generated answer", id="resp-id")

    captured = {}
    class FakeBound:
        def invoke(self, msgs):
            captured['msgs'] = msgs
            return fake_response

    def fake_bind_tools(tools, tool_choice=None):
        return FakeBound()

    monkeypatch.setattr(sql_agent, "llm", SimpleNamespace(bind_tools=fake_bind_tools))

    state = {"messages": [{"role": "user", "content": "How many users?"}]}
    out = sql_agent.generate_query(state)

    assert out["messages"][0].content == "generated answer"
    assert isinstance(captured.get('msgs'), list)
    assert captured['msgs'][0]["role"] == "system"


def test_call_get_schema_forwards_messages(monkeypatch):
    # fake bound LLM that echoes back a response
    fake_response = SimpleNamespace(content="schema result", id="s-id")
    class FakeBound:
        def invoke(self, msgs):
            return fake_response

    def fake_bind_tools(tools, tool_choice=None):
        return FakeBound()

    monkeypatch.setattr(sql_agent, "llm", SimpleNamespace(bind_tools=fake_bind_tools))

    # call_get_schema should pass through the state's messages
    state = {"messages": [{"role": "user", "content": "show schema"}]}
    out = sql_agent.call_get_schema(state)

    assert out["messages"][0].content == "schema result"