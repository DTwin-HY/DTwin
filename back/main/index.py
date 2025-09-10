from flask import Flask, jsonify, request, abort
from flask_cors import CORS
from flask_login import LoginManager, UserMixin
from main.chatgpt.chat import answer
from os import getenv
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from utils import schema

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
db = SQLAlchemy(app)
login_manager = LoginManager
login_manager.init_app(app)

@app.get("/api/ping")
def ping():
    return jsonify({"ok": True, "message": "pong"})

@app.get("/")
def home():
    return (jsonify({"ok": True, "message": "welcome to dtwin!"}))

@app.post("/api/echo")
def echo():
    if not request.is_json:
        abort(400, description="Body must be JSON")
    data = request.get_json()
    print(data)
    output = answer(data["message"])

    sql = text("INSERT INTO logs (prompt, reply) VALUES (:prompt, :reply);")
    db.session.execute(sql, {"prompt":data["message"], "reply": output["message"]})
    db.session.commit()


    return jsonify(output)

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    sql = text("SELECT id, username FROM users WHERE id = :id")
    result = schema.session.execute(sql, {"id" = user_id}).fetchone()
    if result:
        return User(result.id, result.username)
    return None



def start():
    app.run(host="0.0.0.0", port=5000, debug=True)

if __name__ == "__main__":
    start()
