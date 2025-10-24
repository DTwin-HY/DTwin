import uuid
from flask import abort, request, Response, stream_with_context
from flask_login import login_required, current_user

from ..index import app
from ..graph.supervisor import stream_process
from ..database.supervisor_db import create_new_chat

@app.post("/api/supervisor")
@login_required
def supervisor_route():
    if not request.is_json:
        abort(400, description="Body must be JSON")

    data = request.get_json()
    prompt = data.get("message", "").strip()

    thread_id = uuid.uuid4().hex
    def event_stream():
        messages = [{"role": "user", "content": prompt}]
        # assistant_parts = []
        raw = []
        try:
            for sse in stream_process(prompt, thread_id):
                raw.append(sse)      # koko rivi talteen
                yield sse            # striimaa heti
        finally:
            # tässä et yritä parsia — tallennat koko datan
            create_new_chat(
                current_user.id,
                messages + [{"role": "assistant", "content": ""}],  # halutessa tyhjä/placeholder
                thread_id,
                raw_stream="".join(raw),
            )
    return Response(stream_with_context(event_stream()), mimetype="text/event-stream")