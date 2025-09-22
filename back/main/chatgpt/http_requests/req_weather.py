import requests

RAIN_CODES = {51,53,55,56,57,61,63,65,66,67,80,81,82,95,96,99}

<<<<<<< HEAD:back/main/chatgpt/requests/req_weather.py
def fetch_weather(lat, lon):
    """
    Fetch current weather data from Open-Meteo API.
    """
=======
def fetch_weather(location):
    lat, lon = location.get("lat"), location.get("lon")
    print(lat, lon)
>>>>>>> f4b308e (Add weather fetching function to front):back/main/chatgpt/http_requests/req_weather.py
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True,
        "hourly": "precipitation,temperature_2m"
    }
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    cw = data.get("current_weather", {})
    weathercode = cw.get("weathercode")
    return {
        "temp_c": cw.get("temperature"),
        "temperature_2m": cw.get("temperature_2m"),
        "windspeed": cw.get("windspeed"),
        "weathercode": weathercode,
        "is_raining": weathercode in RAIN_CODES,
        "precipitation": cw.get("precipitation"),
        "precipitation_probability": cw.get("precipitation_probability"),
        "rain": cw.get("rain"),
    }
