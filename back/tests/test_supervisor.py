import os
import sys
import types
from pathlib import Path

os.environ.setdefault("TAVILY_API_KEY", "test")

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.index import app  # noqa: E402


@pytest.fixture()
def client():
    app.config.update(TESTING=True, LOGIN_DISABLED=True)
    return app.test_client()


def test_supervisor_streams_and_saves(client, monkeypatch):
    # Import the route module to monkeypatch symbols
    from src.routes import supervisor_route

    # Fake current_user with get_id method
    class FakeUser:
        def __init__(self, user_id):
            self.id = user_id

        def get_id(self):
            return self.id

    monkeypatch.setattr(supervisor_route, "current_user", FakeUser(123), raising=False)

    # Fake stream_process that produces a couple of SSE lines
    def fake_stream(prompt, thread_id):
        assert prompt == "hello"
        assert isinstance(thread_id, str)
        yield 'data: {"step":"one"}\n\n'
        yield 'data: {"step":"two"}\n\n'

    monkeypatch.setattr(supervisor_route, "stream_process", fake_stream)

    saved = {}

    def fake_save(user_id, messages, thread_id, raw_stream=""):
        saved["user_id"] = user_id
        saved["messages"] = messages
        saved["thread_id"] = thread_id
        saved["raw_stream"] = raw_stream

    monkeypatch.setattr(supervisor_route, "create_new_chat", fake_save)

    monkeypatch.setattr(
        supervisor_route,
        "generate_unique_thread_id",
        lambda: "test-thread-id",
        raising=False,
    )

    resp = client.post("/api/supervisor", json={"message": "hello"})
    assert resp.status_code == 200
    assert resp.mimetype == "text/event-stream"

    body = resp.data.decode("utf-8")
    assert 'data: {"step":"one"}' in body
    assert 'data: {"step":"two"}' in body

    # Check that save was called and stream was saved as expected
    assert saved["user_id"] == 123
    assert isinstance(saved["thread_id"], str) and saved["thread_id"]
    assert saved["messages"][0]["role"] == "user"
    assert saved["raw_stream"] == 'data: {"step":"one"}\n\ndata: {"step":"two"}\n\n'


def test_supervisor_rejects_non_json(client):
    resp = client.post("/api/supervisor", data="not json", headers={"Content-Type": "text/plain"})
    assert resp.status_code == 400


def test_fetch_chats_serializes_models(client, monkeypatch):
    from src.routes import chat_route

    # Fake current_user ja get_chats_by_user
    monkeypatch.setattr(chat_route, "current_user", types.SimpleNamespace(id=999), raising=False)

    class FakeChat:
        def __init__(self, id, prompt, response, thread_id):
            self.id = id
            self.prompt = prompt
            self.response = response
            self.thread_id = thread_id

        def to_dict(self):
            return {
                "id": self.id,
                "prompt": self.prompt,
                "response": self.response,
                "thread_id": self.thread_id,
            }

    monkeypatch.setattr(
        chat_route,
        "get_chats_by_user",
        lambda user_id: [FakeChat(1, "p", "r", "t1"), FakeChat(2, "p2", "r2", "t2")],
    )

    resp = client.get("/api/fetch_chats")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "chats" in data and isinstance(data["chats"], list)
    assert data["chats"][0]["id"] == 1
    assert data["chats"][1]["thread_id"] == "t2"


def test_supervisor_uses_client_thread_id(client, monkeypatch):
    from src.routes import supervisor_route

    # Fake current_user
    class FakeUser:
        def __init__(self, user_id):
            self.id = user_id

        def get_id(self):
            return self.id

    monkeypatch.setattr(supervisor_route, "current_user", FakeUser(123), raising=False)

    # Fake Chat-objekti
    class FakeChat:
        def __init__(self, user_id, thread_id):
            self.user_id = user_id
            self.thread_id = thread_id

    client_thread_id = "existing-thread-id-123"

    def fake_get_chat_by_thread_id(thread_id):
        assert thread_id == client_thread_id
        return FakeChat(user_id=123, thread_id=thread_id)

    monkeypatch.setattr(
        supervisor_route, "get_chat_by_thread_id", fake_get_chat_by_thread_id, raising=False
    )

    seen = {"stream_thread_id": None, "saved_thread_id": None}

    def fake_stream(prompt, thread_id):
        assert prompt == "hello"
        seen["stream_thread_id"] = thread_id
        yield 'data: {"step":"one"}\n\n'

    monkeypatch.setattr(supervisor_route, "stream_process", fake_stream)

    def fake_save(user_id, messages, thread_id, raw_stream=""):
        seen["saved_thread_id"] = thread_id
        seen["user_id"] = user_id
        seen["messages"] = messages
        seen["raw_stream"] = raw_stream

    monkeypatch.setattr(supervisor_route, "create_new_chat", fake_save)

    def boom():
        raise AssertionError(
            "generate_unique_thread_id should not be called when valid client_thread_id is provided"
        )

    monkeypatch.setattr(supervisor_route, "generate_unique_thread_id", boom)

    resp = client.post(
        "/api/supervisor",
        json={"message": "hello", "thread_id": client_thread_id},
    )

    assert resp.status_code == 200
    assert resp.mimetype == "text/event-stream"

    body = resp.data.decode("utf-8")

    assert f'"thread_id": "{client_thread_id}"' in body

    assert seen["stream_thread_id"] == client_thread_id
    assert seen["saved_thread_id"] == client_thread_id
    assert seen["user_id"] == 123
    assert seen["messages"][0]["role"] == "user"


def test_supervisor_creates_new_client_thread_id(client, monkeypatch):
    from src.routes import supervisor_route

    # Fake current_user
    class FakeUser:
        def __init__(self, user_id):
            self.id = user_id

        def get_id(self):
            return self.id

    monkeypatch.setattr(supervisor_route, "current_user", FakeUser(123), raising=False)

    # Fake Chat-objekti
    class FakeChat:
        def __init__(self, user_id, thread_id):
            self.user_id = user_id
            self.thread_id = thread_id

    client_thread_id = "existing-thread-id-123"

    def fake_get_chat_by_thread_id(thread_id):
        return None

    monkeypatch.setattr(
        supervisor_route, "get_chat_by_thread_id", fake_get_chat_by_thread_id, raising=False
    )

    seen = {"stream_thread_id": None, "saved_thread_id": None}

    def fake_stream(prompt, thread_id):
        assert prompt == "hello"
        seen["stream_thread_id"] = thread_id
        yield 'data: {"step":"one"}\n\n'

    monkeypatch.setattr(supervisor_route, "stream_process", fake_stream)

    def fake_save(user_id, messages, thread_id, raw_stream=""):
        seen["saved_thread_id"] = thread_id
        seen["user_id"] = user_id
        seen["messages"] = messages
        seen["raw_stream"] = raw_stream

    monkeypatch.setattr(supervisor_route, "create_new_chat", fake_save)

    def new_id():
        return "new_created_id"

    monkeypatch.setattr(supervisor_route, "generate_unique_thread_id", new_id)

    resp = client.post(
        "/api/supervisor",
        json={"message": "hello", "thread_id": client_thread_id},
    )

    assert resp.status_code == 200
    assert resp.mimetype == "text/event-stream"

    body = resp.data.decode("utf-8")

    assert f'"thread_id": "{"new_created_id"}"' in body

    assert seen["stream_thread_id"] == "new_created_id"
    assert seen["saved_thread_id"] == "new_created_id"
    assert seen["user_id"] == 123
    assert seen["messages"][0]["role"] == "user"


def test_stream_process_removal_loop(monkeypatch):
    # Patch supervisor module internals
    import src.graph.supervisor as sup

    # Dummy messages with two consecutive pending tool calls before a non-pending tail
    class Msg:
        def __init__(self, mid, tool_calls=None):
            self.id = mid
            self.tool_calls = tool_calls or []
            self.additional_kwargs = {}

    class Snapshot:
        def __init__(self, msgs):
            self.values = {"messages": msgs}

    class RemoveMessage:
        def __init__(self, id):
            self.id = id

    # Fake PostgresSaver context
    class Saver:
        @classmethod
        def from_conn_string(cls, _):
            return cls()

        def setup(self):  # pragma: no cover
            pass

        def __enter__(self):  # pragma: no cover
            return self

        def __exit__(self, a, b, c):  # pragma: no cover
            return False

    # History: ok-1, pending-a, pending-b, tail
    messages = [
        Msg("ok-1"),
        Msg("pending-a", tool_calls=[{"id": "tc-a"}]),
        Msg("pending-b", tool_calls=[{"id": "tc-b"}]),
        Msg("tail"),
    ]

    class FakeSupervisor:
        def get_state(self, config):
            return Snapshot(messages)

        def update_state(self, config, update):
            # Expect {"messages": [RemoveMessage(id=...)]} and pop last if id matches
            rm = update.get("messages", [None])[0]
            if rm and messages and rm.id == messages[-1].id:
                messages.pop()

        def stream(self, input_state, stream_mode="updates", config=None):
            # After pre-loop, yield one dummy chunk
            yield {"done": True, "len": len(messages)}

    # Patch symbols on module under test
    monkeypatch.setattr(sup, "PostgresSaver", Saver)
    monkeypatch.setattr(sup, "RemoveMessage", RemoveMessage)
    monkeypatch.setattr(sup, "create_agent", lambda **_: FakeSupervisor())
    monkeypatch.setattr(sup, "format_chunk", lambda x: x)

    # Run generator
    gen = sup.stream_process("hello", thread_id="7")
    out = list(gen)
    assert out, "Should stream at least one chunk"

    # The loop removes the last message repeatedly while any pending exists,
    # so it ends up removing tail, then pending-b, then pending-a -> leaving only ok-1.
    ids = [m.id for m in messages]
    assert ids == ["ok-1"]
