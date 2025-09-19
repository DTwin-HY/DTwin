from ..state import GeneralState
from ..requests.req_weather import fetch_weather

def apply_sale(state: GeneralState, sale: dict):
    item_id = sale["item_id"]
    qty = sale["quantity"]
    state["inventory"][item_id]["stock"] -= qty
    state["cash_register"] += state["inventory"][item_id]["price"] * qty
    state["completed_transactions"].append(sale)

# lat=36.0649, lon=120.3804 Qindao location
# lat=60.2094, lon=24.9642 Kumpula location
def set_raining(state: GeneralState):
    weather = fetch_weather(60.2094, 24.9642)
    state["is_raining"] = bool(weather.get("is_raining"))
    return state["is_raining"]