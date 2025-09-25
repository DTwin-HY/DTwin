from datetime import datetime

import requests

RAIN_CODES = {51, 53, 55, 56, 57, 61, 63, 65, 66, 67, 80, 81, 82, 95, 96, 99}


def fetch_weather(lat, lon, date=None):
    """
    Fetch daily weather for given lat/lon (optionally a specific date 'YYYY-MM-DD' or datetime).
    Returns a JSON-serializable dict with is_raining, weathercode, precipitation, coords, date.
    """
    try:
        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": "weather_code,precipitation_sum",
            "timezone": "auto",
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
            "date": date_str,
        }

    except Exception as e:
        print(f"Weather fetch error: {e}")
        return {
            "is_raining": False,
            "weather_code": 0,
            "precipitation": 0,
            "latitude": lat,
            "longitude": lon,
            "date": date_str,
        }
