import os
from types import SimpleNamespace

import pytest

os.environ.setdefault("OPENAI_API_KEY", "test")

import src.services.sql_agent as sql_agent


def test_get_env_or_raise_ok(monkeypatch):
    monkeypatch.setenv("FOO", "bar")
    assert sql_agent._get_env_or_raise("FOO") == "bar"


def make_msg(content="", tool_calls=None, id="mid"):
    if tool_calls is None:
        tool_calls = []
    return SimpleNamespace(content=content, tool_calls=tool_calls, id=id)


def test_should_continue_no_tool_calls():
    state = {"messages": [make_msg(content="hi", tool_calls=[])]}
    res = sql_agent.should_continue_after_generate(state)
    assert res == "analyze_results"


def test_should_continue_with_tool_calls():
    state = {"messages": [make_msg(content="hi", tool_calls=[{"foo": "bar"}])]}
    res = sql_agent.should_continue_after_generate(state)
    assert res == "check_query"


def test_run_sql_agent_invokes_graph(monkeypatch):
    class DummyGraph:
        def invoke(self, _):
            return {"messages": [make_msg("first"), make_msg("final answer")]}

    monkeypatch.setattr(sql_agent, "get_sql_agent_graph", lambda: DummyGraph())
    out = sql_agent.run_sql_agent("SELECT 1")
    assert out == "final answer"


def test_list_tables_uses_correct_tool(monkeypatch):
    def fake_invoke(call):
        return SimpleNamespace(content="users,orders")

    fake_tool = SimpleNamespace(name="sql_db_list_tables", invoke=fake_invoke)

    class FakeToolkit:
        def get_tools(self):
            return [fake_tool]

    monkeypatch.setattr(sql_agent, "_make_toolkit", lambda: FakeToolkit())

    res = sql_agent.list_tables({"messages": []})
    assert isinstance(res, dict) and "messages" in res
    msgs = res["messages"]
    assert len(msgs) == 3
    assert "Available tables" in msgs[-1].content


def _patch_llm_and_toolkit(monkeypatch, response_text="ok"):
    """Yleispatch: LLM.bind_tools().invoke() palauttaa halutun vastauksen,
    toolkit tarjoaa db.dialect sekä run/list/schema -työkalut niminä."""
    fake_response = SimpleNamespace(content=response_text, id=None)

    class FakeBound:
        def invoke(self, msgs):
            return fake_response

    class FakeLLM:
        def bind_tools(self, tools, tool_choice=None):
            return FakeBound()

    class FakeTool:
        def __init__(self, name):
            self.name = name

        def invoke(self, call):
            return SimpleNamespace(content="stub")

    class FakeToolkit:
        def __init__(self):
            self.db = SimpleNamespace(dialect="sqlite")

        def get_tools(self):
            return [
                FakeTool("sql_db_query"),
                FakeTool("sql_db_schema"),
                FakeTool("sql_db_list_tables"),
            ]

    monkeypatch.setattr(sql_agent, "_make_llm", lambda: FakeLLM())
    monkeypatch.setattr(sql_agent, "_make_toolkit", lambda: FakeToolkit())
    return fake_response


def test_check_query_sets_response_id(monkeypatch):
    fake_resp = _patch_llm_and_toolkit(monkeypatch, response_text="checked query")

    last_msg = make_msg(
        content="",
        tool_calls=[{"args": {"query": "SELECT 1"}}],
        id="orig-id",
    )
    state = {"messages": [last_msg]}

    out = sql_agent.check_query(state)
    msg = out["messages"][0]
    assert msg.id == "orig-id"
    assert msg.content == "checked query"


def test_generate_query_invokes_llm(monkeypatch):
    captured = {}

    class FakeResponse(SimpleNamespace):
        pass

    fake_response = FakeResponse(content="generated answer", id="resp-id")

    class FakeBound:
        def invoke(self, msgs):
            captured["msgs"] = msgs
            return fake_response

    class FakeLLM:
        def bind_tools(self, tools, tool_choice=None):
            return FakeBound()

    class FakeTool:
        def __init__(self, name):
            self.name = name

        def invoke(self, call):
            return SimpleNamespace(content="stub")

    class FakeToolkit:
        def __init__(self):
            self.db = SimpleNamespace(dialect="sqlite")

        def get_tools(self):
            return [FakeTool("sql_db_query")]

    monkeypatch.setattr(sql_agent, "_make_llm", lambda: FakeLLM())
    monkeypatch.setattr(sql_agent, "_make_toolkit", lambda: FakeToolkit())

    state = {"messages": [{"role": "user", "content": "How many users?"}]}
    out = sql_agent.generate_query(state)

    assert out["messages"][0].content == "generated answer"
    assert isinstance(captured.get("msgs"), list)
    assert captured["msgs"][0]["role"] == "system"


def test_call_get_schema_forwards_messages(monkeypatch):
    fake_response = SimpleNamespace(content="schema result", id="s-id")

    class FakeBound:
        def invoke(self, msgs):
            assert msgs[-1]["content"] == "show schema"
            return fake_response

    class FakeLLM:
        def bind_tools(self, tools, tool_choice=None):
            return FakeBound()

    class FakeTool:
        def __init__(self, name):
            self.name = name

        def invoke(self, call):
            return SimpleNamespace(content="stub")

    class FakeToolkit:
        def __init__(self):
            self.db = SimpleNamespace(dialect="sqlite")

        def get_tools(self):
            return [FakeTool("sql_db_schema")]

    monkeypatch.setattr(sql_agent, "_make_llm", lambda: FakeLLM())
    monkeypatch.setattr(sql_agent, "_make_toolkit", lambda: FakeToolkit())

    state = {"messages": [{"role": "user", "content": "show schema"}]}
    out = sql_agent.call_get_schema(state)
    assert out["messages"][0].content == "schema result"


def test_should_retry_query_no_tools():
    state = {"messages": []}
    assert sql_agent.should_retry_query(state) == "analyze_results"


def test_should_retry_query_with_error_tool():
    msg = SimpleNamespace(type="tool", content="Some error occurred")
    state = {"messages": [msg]}
    assert sql_agent.should_retry_query(state) == "generate_query"


def test_should_retry_query_max_queries():
    msg1 = SimpleNamespace(type="tool", content="stub query sql_db_query")
    msg2 = SimpleNamespace(type="tool", content="stub query sql_db_query")
    state = {"messages": [msg1, msg2]}
    assert sql_agent.should_retry_query(state) == "analyze_results"


def test_analyze_results_returns_ai_message(monkeypatch):
    class FakeLLM:
        def invoke(self, msgs):
            return SimpleNamespace(content="final answer", id=None)

    monkeypatch.setattr(sql_agent, "_make_llm", lambda: FakeLLM())

    state = {"messages": [SimpleNamespace(content="some data")]}
    result = sql_agent.analyze_results(state)
    assert isinstance(result, dict)
    msg = result["messages"][0]
    assert hasattr(msg, "content")
    assert msg.content == "final answer"


def test_should_retry_query_edge(monkeypatch):
    msg = SimpleNamespace(type="other", content="Some error occurred")
    state = {"messages": [msg]}
    assert sql_agent.should_retry_query(state) == "analyze_results"


def test_analyze_results_empty_state(monkeypatch):
    class FakeLLM:
        def invoke(self, msgs):
            return SimpleNamespace(content="no data", id=None)

    monkeypatch.setattr(sql_agent, "_make_llm", lambda: FakeLLM())
    state = {"messages": []}
    out = sql_agent.analyze_results(state)
    assert out["messages"][0].content == "no data"


def test_make_llm_and_toolkit_types(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    llm = sql_agent._make_llm()
    toolkit = sql_agent._make_toolkit()
    from langchain_community.agent_toolkits import SQLDatabaseToolkit
    from langchain_openai import ChatOpenAI

    assert isinstance(llm, ChatOpenAI)
    assert isinstance(toolkit, SQLDatabaseToolkit)
