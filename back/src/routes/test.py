<<<<<<< HEAD
from flask import abort, jsonify, request
from flask_login import login_required
from sqlalchemy.sql import text

from main.chatgpt.chat import answer
=======
from flask import jsonify, request, abort
from flask_login import login_required
from sqlalchemy.sql import text
<<<<<<< HEAD:back/main/routes/test.py
from ..simulation.chat import answer
from back.index import app, db
>>>>>>> f31294b (Refactor the backend and removed useless imports)

from ..index import app, db

=======
from src.simulation.chat import answer
from ..index import app, db
>>>>>>> 898d943 (Fix imports to work with -m flag, rename main folder to src for clarity):back/src/routes/test.py

@app.get("/api/ping")
def ping():
    return jsonify({"ok": True, "message": "pong"})


@app.get("/")
def home():
<<<<<<< HEAD:back/main/routes/test.py
    return jsonify({"ok": True, "message": "welcome to dtwin!"})

=======
    print("lol")
    return (jsonify({"ok": True, "message": "welcome to dtwin!"}))
>>>>>>> 898d943 (Fix imports to work with -m flag, rename main folder to src for clarity):back/src/routes/test.py

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
