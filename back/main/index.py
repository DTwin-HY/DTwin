from flask import Flask, jsonify, request, abort
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user
from main.chatgpt.chat import answer
from os import getenv
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from flask_bcrypt import Bcrypt

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
bcrypt = Bcrypt(app)

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

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    username = data["username"]
    password = data["password"]

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already taken"})

    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User created"})

@app.route("/signin", methods=["POST"])
def signin():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error: Username and password required"})

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "Invalid username or password"})
    if not bcrypt.check_password_has(user.password, password):
        return jsonify({"error": "Invalid username or password"})

    login_user(user)
    return jsonify({"message": "Login successful! Welcome", "username": user.username})

def start():
    app.run(host="0.0.0.0", port=5000, debug=True)

if __name__ == "__main__":
    start()
