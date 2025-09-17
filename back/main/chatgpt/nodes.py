import json
from langchain_core.messages import HumanMessage
from main.chatgpt.llm_utils import call_llm
from main.chatgpt.prompts import SELLER_PROMPT, CUSTOMER_PROMPT
from main.chatgpt.state import ConversationState

def apply_sale(state: ConversationState, sale: dict):
    item_id = sale["item_id"]
    qty = sale["quantity"]
    state["inventory"][item_id]["stock"] -= qty
    state["cash_register"] += state["inventory"][item_id]["price"] * qty
    state["completed_transactions"].append(sale)

def seller_node(state: ConversationState) -> ConversationState:
    prompt = f"{SELLER_PROMPT}\n\nInventory: {json.dumps(state['inventory'])}\nConversation: {state['messages']}"
    resp = call_llm(prompt, expect_json=True)

    items_text = []
    for sale in resp.get("berries_sold", []):
        item_id = sale["item_id"]
        qty = sale["quantity"]
        name = state["inventory"][item_id]["name"]
        items_text.append(f"{qty} x {name}")

    if items_text:
        total = sum(state["inventory"][sale["item_id"]]["price"] * sale["quantity"] for sale in resp["berries_sold"])
        response_text = f"Sale complete: {', '.join(items_text)}. Total: ${total:.2f}."
    else:
        response_text = resp["response"]
        for item_id, info in state["inventory"].items():
            response_text = response_text.replace(item_id, info["name"])

    msg = "Seller: " + response_text
    state["messages"].append(HumanMessage(content=msg))
    print(msg)

    for sale in resp.get("berries_sold", []):
        apply_sale(state, sale)

    state["conversation_active"] = resp["conversation_should_continue"]
    state["conversation_turn"] += 1
    return state

def customer_node(state: ConversationState) -> ConversationState:
    prompt = f"{CUSTOMER_PROMPT}\n\nConversation: {state['messages']}"
    resp = call_llm(prompt)

    msg = "Customer: " + resp
    state["messages"].append(HumanMessage(content=msg))
    state["conversation_turn"] += 1
    print(msg)
    return state