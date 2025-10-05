import random
from typing import Dict, Any
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from datetime import datetime, timezone
from .state import GeneralState, LogEntry
from .llm_utils import OPENAI_API_KEY
from .helper_nodes import update_inventory, update_cash_register, add_log


MAX_PER_CUSTOMER = 3  # Max items per customer
SMALL_PROB = 0.6  # Probability a customer chooses a small item
MEDIUM_PROB = 0.4  # Probability a customer chooses a medium item
BUY_PROB = {True: 0.3, False: 0.7} # Probability a customer buys any item, depending on rain
CUSTOMER_RANGE = {True: (10, 30), False: (20, 50)} # Customer count depending on rain

def init_state() -> GeneralState:
    """
    Initialize the general state for the sales simulation.
    Includes cash register, inventory, logs, and supervisor conversation.
    """
    return {
        "cash_register": 100,
        "logs": [],
        "is_raining": False,
        "supervisor_conversation": [],
        "small_sold": 0,
        "medium_sold": 0,
        "inventory": {
            1: {"product_id": 1, "name": "Small Box of Strawberries", "quantity": 50, "price": 3.0,},
            2: {"product_id": 2, "name": "Medium Box of Strawberries", "quantity": 30, "price": 5.0},
        },
    }

def process_sale(state: GeneralState, item_id: int) -> float:
    item = state["inventory"][item_id]

    if item["quantity"] <= 0:
        return 0.0

    state = update_inventory(state, item_id, -1)
    price = item["price"]
    state = update_cash_register(state, price)


    log_entry: LogEntry = {
        "product_id": str(item_id),
        "amount": price,
        "event_type": "sale",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    state = add_log(state, log_entry)

    return price


@tool("simulate_sales")
def simulate_sales() -> Dict[str, Any]:
    """
    Simulates sales for the current state, updating inventory and cash register.
    This tool doesn't take any parameters - it uses the current state.
    """
    state = init_state()
    is_raining =state.get("is_raining", False)
    customers = random.randint(*CUSTOMER_RANGE[is_raining])
    buy_prob = BUY_PROB[is_raining]

    small_sold, medium_sold = 0, 0

    for _ in range(customers):
        if random.random() < buy_prob:
            num_items = random.randint(1, MAX_PER_CUSTOMER)
            for _ in range(num_items):
                item_type = 1 if random.random() < SMALL_PROB else 2
                if state["inventory"][item_type]["quantity"] > 0:
                    process_sale(state, item_type)
                    if item_type == 1:
                        small_sold += 1
                    else:
                        medium_sold += 1
    result = {
        "small_sold": small_sold,
        "medium_sold": medium_sold,
        "cash_register": state["cash_register"],
        "inventory": state["inventory"],
        "message": f"Simulation complete: {small_sold} small and {medium_sold} medium items sold, Cash register: {state['cash_register']}"
    }
    return result


def build_seller_agent():
    seller_agent = create_react_agent(
        model=ChatOpenAI(model="gpt-5-nano", api_key=OPENAI_API_KEY),
        tools=[simulate_sales],
        prompt=(
            "You are a seller agent responsible for simulating sales at a stand.\n"
            "INSTRUCTIONS:\n"
            "- When asked to simulate sales, use the simulate_sales tool once to do a simulation.\n"
            "- The tool doesn't require any parameters - just call it. \n"
            "- Return only the results of the simulation to the supervisor."
        ),
        name="seller_agent",
    )
    return seller_agent