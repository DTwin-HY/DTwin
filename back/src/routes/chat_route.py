from flask_login import login_required, current_user
from flask import jsonify
from datetime import date, datetime

from ..index import app
from ..database.supervisor_db import get_chats_by_user

def _model_to_dict(obj):
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    data = {}
    for col in obj.__table__.columns:
        val = getattr(obj, col.name)
        if isinstance(val, (datetime, date)):
            val = val.isoformat()
        data[col.name] = val
    return data

@app.get("/api/fetch_chats")
@login_required
def fetch_chats():
    user_id = current_user.id
    chats = get_chats_by_user(user_id)
    return jsonify({"chats": [_model_to_dict(c) for c in chats]})