<<<<<<< HEAD
from flask import jsonify, request
from flask_login import login_required

from main.chatgpt.requests.req_weather import fetch_weather

from ..index import app

=======
from back.index import app
from flask import jsonify, request
from flask_login import login_required
from ..http_requests.req_weather import fetch_weather
>>>>>>> f31294b (Refactor the backend and removed useless imports)

@app.post("/api/weather")
@login_required
def get_weather():
    data = request.json
    lat = data.get("lat")
    lon = data.get("lon")
    date = data.get("date")

    if lat is None or lon is None:
        return jsonify({"error": "lat and lon required"}), 400

    weather = fetch_weather(lat, lon, date)
    return jsonify(weather)
