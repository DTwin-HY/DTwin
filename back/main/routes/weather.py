from back.index import app
from flask import jsonify, request
from flask_login import login_required
from ..http_requests.req_weather import fetch_weather

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