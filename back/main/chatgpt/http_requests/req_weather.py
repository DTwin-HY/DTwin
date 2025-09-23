import requests
from datetime import datetime, timedelta

RAIN_CODES = {51,53,55,56,57,61,63,65,66,67,80,81,82,95,96,99}

<<<<<<< HEAD
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
=======
import requests
from datetime import datetime, timedelta

RAIN_CODES = {51,53,55,56,57,61,63,65,66,67,80,81,82,95,96,99}

def fetch_weather(lat, lon, date=None):
    try:
        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": "weather_code,precipitation_sum",
            "timezone": "auto"
        }

        if date:
            date_str = date if isinstance(date, str) else date.strftime("%Y-%m-%d")
            params["start_date"] = date_str
            params["end_date"] = date_str
        else:
            date_str = datetime.now().strftime("%Y-%m-%d")

        url = "https://api.open-meteo.com/v1/forecast"
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        daily = data.get("daily", {})
        weather_code = daily.get("weather_code", [0])[0]
        precipitation = daily.get("precipitation_sum", [0])[0]
        is_raining = precipitation > 0 or weather_code in RAIN_CODES

        return {
            "is_raining": is_raining,
            "weather_code": weather_code,
            "precipitation": precipitation,
            "latitude": lat,
            "longitude": lon,
            "date": date_str
        }

    except Exception as e:
        print(f"Weather fetch error: {e}")
        return {
            "is_raining": False,
            "weather_code": 0,
            "precipitation": 0,
            "latitude": lat,
            "longitude": lon,
            "date": date_str
        }
>>>>>>> f212a85 (Add weather feature to future date simulation)
