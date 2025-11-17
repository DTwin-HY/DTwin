import sys
from pathlib import Path

import types
import json
import pytest

# Add back/src to import path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))


# ---- Fixtures and dummies ----------------------------------------------------


class DummySnapshot:
    def __init__(self, messages):
        self.values = {"messages": list(messages)}


class AssistantMsg:
    def __init__(self, id, tool_calls=None, additional_kwargs=None, content=""):
        self.id = id
        self.content = content
        self.tool_calls = tool_calls or []
        self.additional_kwargs = additional_kwargs or {}


class ToolMessage:
    # Only shape the code under test probes: class name and tool_call_id
    def __init__(self, tool_call_id, content="ok"):
        self.tool_call_id = tool_call_id
        self.content = content


@pytest.fixture
def fake_supervisor_obj(monkeypatch):
    """
    A fake 'supervisor' returned by create_agent with:
    - get_state/config -> DummySnapshot of current messages
    - update_state -> removes last message when given a RemoveMessage
    - stream -> yields one json chunk (after the pending removal)
    """
    # Initial history where the last message requests a tool call (pending)
    msgs = [
        AssistantMsg("m1", tool_calls=[]),
        AssistantMsg("m2", tool_calls=[{"id": "tc-1"}]),  # pending tool call
    ]
    state = {"messages": msgs}

    class FakeSupervisor:
        def get_state(self, config):
            return DummySnapshot(state["messages"])

        def update_state(self, config, data):
            # Expect {"messages": [RemoveMessage(id=...)]}; pop last message
            rm = data.get("messages", [None])[0]
            # Remove only if it's the last
            if state["messages"] and getattr(rm, "id", None) == state["messages"][-1].id:
                state["messages"].pop()

        def stream(self, input_state, stream_mode="updates", config=None):
            # After removal, produce one simple chunk
            yield {"ok": True, "state_len": len(state["messages"])}

    return FakeSupervisor(), state


@pytest.fixture
def patch_supervisor_module(monkeypatch, fake_supervisor_obj):
    """
    Patch src.graph.supervisor:
    - PostgresSaver.from_conn_string -> dummy ctx mgr
    - create_agent -> FakeSupervisor
    - RemoveMessage -> simple class with .id
    - format_chunk -> identity
    """
    import src.graph.supervisor as sup

    class DummySaver:
        @classmethod
        def from_conn_string(cls, _):
            return cls()

        def setup(self):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    # Simple RemoveMessage replacement
    class _RemoveMessage:
        def __init__(self, id):
            self.id = id

    fake_supervisor, _state = fake_supervisor_obj

    monkeypatch.setattr(sup, "PostgresSaver", DummySaver)
    monkeypatch.setattr(sup, "create_agent", lambda **kwargs: fake_supervisor)
    monkeypatch.setattr(sup, "RemoveMessage", _RemoveMessage)
    monkeypatch.setattr(sup, "format_chunk", lambda x: x)

    return sup, _state


# ---- Tests for utils.check_pending_tool_call ---------------------------------


def test_check_pending_tool_call_any_pending_true_false():
    from src.utils.check_pending_tool_call import check_pending_tool_call

    # History: assistant called tool tc-a and got answered; later tc-b pending, no answer
    history = [
        AssistantMsg("a1", tool_calls=[{"id": "tc-a"}]),
        ToolMessage(tool_call_id="tc-a"),
        AssistantMsg("a2", tool_calls=[{"id": "tc-b"}]),  # pending
    ]
    snap = DummySnapshot(history)
    assert check_pending_tool_call(snap) is True

    # Add response for tc-b -> no pending
    history.append(ToolMessage(tool_call_id="tc-b"))
    snap2 = DummySnapshot(history)
    assert check_pending_tool_call(snap2) is False

    # No tool calls at all
    snap3 = DummySnapshot([AssistantMsg("z")])
    assert check_pending_tool_call(snap3) is False


# ---- Test for the supervisor snippet (pending removal) -----------------------


def test_supervisor_removes_last_pending_before_stream(monkeypatch, patch_supervisor_module, fake_supervisor_obj):
    sup, state = patch_supervisor_module
    fake_supervisor, _ = fake_supervisor_obj

    # Sanity: last message has pending tool_calls before stream
    assert state["messages"][-1].tool_calls, "Precondition failed: should start with pending tool call"

    # Drive the generator
    gen = sup.stream_process(prompt="hello", thread_id="t1")
    out = list(gen)

    # After the pre-loop, the last message should have been removed
    assert len(state["messages"]) == 1
    assert state["messages"][-1].id == "m1"

    # Stream yielded one SSE line with our chunk
    assert out, "Expected at least one streamed SSE line"
    payload = out[0].removeprefix("data: ").strip()
    assert payload.endswith("\n\n") is False  # .stream_process already includes the \n\n when yielding
    data = json.loads(payload)
    assert data["ok"] is True
    assert data["state_len"] == 1
