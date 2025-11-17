from ..extensions import db
from ..models.models import Chat


def create_new_chat(user_id, messages, thread_id, raw_stream):
    """
    Create or update a chat in the database.

    - If a Chat with the given thread_id exists, update its messages and raw_stream
      (and user_id if different), then commit and return the existing row.
    - Otherwise, create a new Chat row and return it.
    """
    existing = Chat.query.filter_by(thread_id=thread_id).first()
    if existing:
        # Update fields on the existing chat
        existing.user_id = user_id
        existing.messages = messages
        existing.raw_stream = raw_stream
        db.session.add(existing)
        db.session.commit()
        return existing

    new_chat = Chat(user_id=user_id, messages=messages, thread_id=thread_id, raw_stream=raw_stream)
    db.session.add(new_chat)
    db.session.commit()

    return new_chat


def get_chats_by_user(user_id):
    """
    Retrieve all chats for a given user.
    """
    return Chat.query.filter_by(user_id=user_id).all()

def check_thread_id_exists(thread_id):
    """
    Check if a chat with the given thread_id exists.
    """
    existing = Chat.query.filter_by(thread_id=thread_id).first()
    return existing is not None
