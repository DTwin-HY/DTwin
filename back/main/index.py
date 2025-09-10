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
login_manager = LoginManager(db)

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

class User(UserMixin, db.model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.column(db.String(250), unique=True, nullable=False)
    password = db.column(db.String(250), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def start():
    app.run(host="0.0.0.0", port=5000, debug=True)

if __name__ == "__main__":
    start()
