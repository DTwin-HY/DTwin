import uuid

from flask import Response, abort, request, stream_with_context
from flask_login import current_user, login_required

from ..database.supervisor_db import create_new_chat
from ..graph.supervisor import stream_process
from ..index import app


@app.post("/api/supervisor")
@login_required
def supervisor_route():
    if not request.is_json:
        abort(400, description="Body must be JSON")

    data = request.get_json()
    prompt = data.get("message", "").strip()

    # thread_id = uuid.uuid4().hex
    thread_id = str(current_user.get_id())

    def event_stream():
        messages = [{"role": "user", "content": prompt}]
        # assistant_parts = []
        raw = []
        try:
            for sse in stream_process(prompt, thread_id):
                raw.append(sse)  # koko rivi talteen
                yield sse  # striimaa heti
        finally:
            # tässä et yritä parsia — tallennat koko datan
            create_new_chat(
                current_user.id,
                messages + [{"role": "assistant", "content": ""}],  # halutessa tyhjä/placeholder
                thread_id,
                raw_stream="".join(raw),
            )

    return Response(stream_with_context(event_stream()), mimetype="text/event-stream")
