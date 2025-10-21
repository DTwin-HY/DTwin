from flask import abort, request, Response
from flask_login import login_required

from ..index import app
from src.graph.supervisor import stream_process

@app.post("/api/supervisor")
@login_required
def supervisor_route():
    if not request.is_json:
        abort(400, description="Body must be JSON")

    data = request.get_json()
    prompt = data.get("message", "").strip()
    if not prompt:
        abort(400, description="Missing 'message'")

    return Response(stream_process(prompt), mimetype="text/event-stream")