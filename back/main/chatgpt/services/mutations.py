from ..state import GeneralState
from ..requests.req_weather import fetch_weather
from main.index import app, db
from datetime import datetime
from sqlalchemy import text

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
def set_raining(state: GeneralState):
    weather = fetch_weather(60.2094, 24.9642)
    state["is_raining"] = bool(weather.get("is_raining"))
    return state["is_raining"]