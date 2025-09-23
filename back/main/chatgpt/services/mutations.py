from ..state import GeneralState
from ..http_requests.req_weather import fetch_weather
from datetime import datetime, timedelta
from sqlalchemy import text
from flask import current_app
from flask_sqlalchemy import SQLAlchemy

def apply_sale(state: GeneralState, sale: dict, transaction_id: str):
    item_id = sale["item_id"]
    qty = sale["quantity"]
    price = state["inventory"][item_id]["price"]
    amount = price * qty

    state["inventory"][item_id]["stock"] -= qty
    state["cash_register"] += amount
    sale["timestamp"] = datetime.now()
    sale["amount"] = amount
    sale["transaction_id"] = transaction_id
    state["completed_transactions"].append(sale)

    from main.index import app, db

    with app.app_context():
        sql = text("""INSERT INTO sales (transaction_id, item_id, quantity, amount, timestamp)
                      VALUES (:transaction_id, :item_id, :quantity, :amount, :timestamp)""")
        db.session.execute(sql, {"transaction_id": transaction_id,
                                "item_id": item_id,
                                "quantity": qty,
                                "amount": amount,
                                "timestamp": sale["timestamp"]})
        db.session.commit()

# lat=36.0649, lon=120.3804 Qindao location
# lat=60.2094, lon=24.9642 Kumpula location
def set_raining(state: GeneralState = None, lat=None, lon=None):
    if state and "lat" in state:
        lat = lat or state["lat"]
        lon = lon or state["lon"]

    lat = lat or 60.2094
    lon = lon or 24.9624

    date = None
    if state and "simulation_date" in state:
        today = datetime.now().date()
        max_forecast_date = today + timedelta(days=7)
        if state["simulation_date"].date() <= max_forecast_date:
            date = state["simulation_date"].strftime("%Y-%m-%d")

    weather = fetch_weather(lat, lon, date=date)

    if state:
        state["is_raining"] = bool(weather.get("is_raining"))

    return bool(weather.get("is_raining"))
