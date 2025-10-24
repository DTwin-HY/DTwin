from ..index import db
from ..models.models import Chat

def create_new_chat(user_id, messages, thread_id, raw_stream):
    """
    Create a new chat in the database.
    """
    new_chat = Chat(user_id=user_id, messages=messages, thread_id=thread_id, raw_stream=raw_stream)
    db.session.add(new_chat)
    db.session.commit()

    return new_chat