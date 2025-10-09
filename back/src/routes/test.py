from flask import abort, jsonify, request
from flask_login import login_required
from sqlalchemy.sql import text

from src.simulation.chat import answer

from ..index import app, db


@app.get("/api/ping")
def ping():
    return jsonify({"ok": True, "message": "pong"})


@app.get("/")
def home():
    return jsonify({"ok": True, "message": "welcome to dtwin!"})


@app.post("/api/echo")
@login_required
def echo():
    if not request.is_json:
        abort(400, description="Body must be JSON")
    data = request.get_json()
    print(data)
    output = answer(data["message"])

    sql = text("INSERT INTO logs (prompt, reply) VALUES (:prompt, :reply);")
    db.session.execute(sql, {"prompt": data["message"], "reply": output["message"]})
    db.session.commit()

    return jsonify(output)
