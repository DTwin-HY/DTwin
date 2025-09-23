from ..state import GeneralState
from ..requests.req_weather import fetch_weather
from datetime import datetime
from sqlalchemy import text
from flask import current_app
from flask_sqlalchemy import SQLAlchemy

from main.models import db

def apply_sale(state: GeneralState, sale: dict, transaction_id: str):
    """
    update state with the given sale and log it to the database
    """
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

    try:
        # Try to access current_app to see if we're in a context
        current_app.name
        
        sql = text("""INSERT INTO sales (transaction_id, item_id, quantity, amount, timestamp)
                      VALUES (:transaction_id, :item_id, :quantity, :amount, :timestamp)""")
        db.session.execute(sql, {"transaction_id": transaction_id,
                                "item_id": item_id,
                                "quantity": qty,
                                "amount": amount,
                                "timestamp": sale["timestamp"]})
        db.session.commit()
    except RuntimeError:
        # No app context - we need to create one
        from main.index import app
        with app.app_context():
            sql = text("""INSERT INTO sales (transaction_id, item_id, quantity, amount, timestamp)
                          VALUES (:transaction_id, :item_id, :quantity, :amount, :timestamp)""")
            db.session.execute(sql, {"transaction_id": transaction_id,
                                    "item_id": item_id,
                                    "quantity": qty,
                                    "amount": amount,
                                    "timestamp": sale["timestamp"]})
            db.session.commit()

def set_raining(state: GeneralState, coords: tuple=(60.2094, 24.9642)):
    """
    set state["is_raining"] based on weather at given coordinates
    default coords are for Kumpula, Helsinki

    lat=36.0649, lon=120.3804 Qindao location
    lat=60.2094, lon=24.9642 Kumpula location
    """
    weather = fetch_weather(*coords)
    state["is_raining"] = bool(weather.get("is_raining"))
    return state["is_raining"]