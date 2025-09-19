from ..state import GeneralState
import random
def apply_sale(state: GeneralState, sale: dict):
    item_id = sale["item_id"]
    qty = sale["quantity"]
    state["inventory"][item_id]["stock"] -= qty
    state["cash_register"] += state["inventory"][item_id]["price"] * qty
    state["completed_transactions"].append(sale)

def set_raining(state: GeneralState):
    if random.random() < 0.4:  # 30% chance of rain
        state["is_raining"] = True
    return state["is_raining"]