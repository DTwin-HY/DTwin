from flask import jsonify

from ..index import app


@app.get("/api/ping")
def ping():
    return jsonify({"ok": True, "message": "pong"})


@app.get("/")
def home():
    return jsonify({"ok": True, "message": "welcome to dtwin!"})
