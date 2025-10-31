import os
import importlib
import pytest
from ..src.extensions import db
from ..src.models.models import User
from ..src.database.supervisor_db import create_new_chat, get_chats_by_user


@pytest.fixture
def app():
    # conftest juostaan ensin ja vasta sen jälkeen importataan index
    from ..src import index as index_mod
    importlib.reload(index_mod)  # varmistaa että lukee environmentin
    app = index_mod.app

    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]

    with app.app_context():
        db.create_all()
        # kun testit on tehty, pudotetaan taulut
        yield app
        db.session.remove()  # tärkeä ennen drop_all()
        db.drop_all()


@pytest.fixture
def test_user(app):
    """Create a test user."""
    with app.app_context():
        user = User(username="testuser", password="hashedpass123")
        db.session.add(user)
        db.session.commit()
        return db.session.get(User, user.id)

class TestSupervisorDB:
    def test_create_new_chat(self, app, test_user):
        """Test creating a new chat."""
        with app.app_context():
            messages = [{"role": "user", "content": "test message"}]
            chat = create_new_chat(
                user_id=test_user.id,
                messages=messages,
                thread_id="test-thread-123",
                raw_stream="test stream data"
            )

            assert chat.user_id == test_user.id
            assert chat.messages == messages
            assert chat.thread_id == "test-thread-123"
            assert chat.raw_stream == "test stream data"

    def test_create_new_chat_updates_existing(self, app, test_user):
        """Test that create_new_chat updates existing chat with same thread_id."""
        with app.app_context():
            # Create initial chat
            messages1 = [{"role": "user", "content": "first message"}]
            chat1 = create_new_chat(
                user_id=test_user.id,
                messages=messages1,
                thread_id="same-thread",
                raw_stream="first stream"
            )

            # Create/update chat with same thread_id
            messages2 = [{"role": "user", "content": "second message"}]
            chat2 = create_new_chat(
                user_id=test_user.id,
                messages=messages2,
                thread_id="same-thread",
                raw_stream="second stream"
            )

            # Should update existing chat, not create new one
            assert chat1.id == chat2.id
            assert chat2.messages == messages2
            assert chat2.raw_stream == "second stream"

    def test_get_chats_by_user(self, app, test_user):
        """Test retrieving all chats for a user."""
        with app.app_context():
            # Create two chats for the user
            create_new_chat(
                user_id=test_user.id,
                messages=[{"role": "user", "content": "chat 1"}],
                thread_id="thread-1",
                raw_stream="stream 1"
            )
            create_new_chat(
                user_id=test_user.id,
                messages=[{"role": "user", "content": "chat 2"}],
                thread_id="thread-2",
                raw_stream="stream 2"
            )

            # Get all chats for the user
            chats = get_chats_by_user(test_user.id)
            
            assert len(chats) == 2
            assert all(chat.user_id == test_user.id for chat in chats)
            assert {chat.thread_id for chat in chats} == {"thread-1", "thread-2"}