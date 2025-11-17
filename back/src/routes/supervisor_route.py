import json

from flask import Response, abort, request, stream_with_context
from flask_login import current_user, login_required

from ..database.supervisor_db import create_new_chat, get_chat_by_thread_id
from ..graph.supervisor import stream_process
from ..index import app
from ..utils.generate_thread_id import generate_unique_thread_id


@app.post("/api/supervisor")
@login_required
def supervisor_route():
    if not request.is_json:
        abort(400, description="Body must be JSON")

    data = request.get_json()
    prompt = data.get("message", "").strip()

    # Get thread id from frontend
    client_thread_id = data.get("thread_id")

    thread_id = None

    if client_thread_id:
        existing_chat = get_chat_by_thread_id(client_thread_id)
        # Continuing an existing chat
        if existing_chat and existing_chat.user_id == current_user.id:
            # OK → tämä thread kuuluu tälle userille
            thread_id = client_thread_id
            print(f"Continuing chat with existing thread_id: {thread_id}")
        else:
            # Either no such chat or belongs to another user → ÄLÄ käytä
            print("Client supplied invalid or foreign thread_id, creating a new one")
            thread_id = generate_unique_thread_id()
    else:
        # New chat → create a new unique id
        print("Starting a new chat with a new thread_id")
        thread_id = generate_unique_thread_id()

    def event_stream():
        messages = [{"role": "user", "content": prompt}]
        raw = []

        meta_event = {"thread_id": thread_id}
        yield f"event: thread_id\ndata: {json.dumps(meta_event)}\n\n"

        try:
            for sse in stream_process(prompt, thread_id):
                raw.append(sse)
                yield sse
        finally:
            # Saves the chat to the database when done
            create_new_chat(
                current_user.id,
                messages + [{"role": "assistant", "content": ""}],  # halutessa tyhjä/placeholder
                thread_id,
                raw_stream="".join(raw),
            )

    return Response(stream_with_context(event_stream()), mimetype="text/event-stream")
