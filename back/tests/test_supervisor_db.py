import pytest
from ..src.database.supervisor_db import create_new_chat, get_chats_by_user
from ..src.models.models import User, Chat
from ..src.extensions import db

@pytest.fixture
def app():
    """Create a Flask application for testing."""
    from ..src.index import app
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
    
    with app.app_context():
        db.create_all()
        yield app
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