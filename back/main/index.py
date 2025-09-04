from flask import Flask, jsonify, request, abort
from flask_cors import CORS
from chatgpt.chat import answer
from sqlalchemy.sql import text
from os import getenv
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
db = SQLAlchemy(app)

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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
