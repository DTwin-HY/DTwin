from flask import Flask, jsonify, request, abort
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

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
    return jsonify({"you_sent": data})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
