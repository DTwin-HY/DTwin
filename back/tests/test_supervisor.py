import os
import sys
import types
from pathlib import Path

# Aseta testitietokanta ennen app-importia
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("TAVILY_API_KEY", "test")

import pytest

# Lisää back/src import-pathiin
sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from back.src.index import app  # noqa: E402


@pytest.fixture()
def client():
    app.config.update(TESTING=True, LOGIN_DISABLED=True)
    return app.test_client()


def test_supervisor_streams_and_saves(client, monkeypatch):
    # Import the route module to monkeypatch symbols
    from back.src.routes import supervisor_route

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
    from back.src.routes import chat_route

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