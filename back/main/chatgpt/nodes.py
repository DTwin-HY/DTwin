import json
from langchain_core.messages import HumanMessage
from main.chatgpt.llm_utils import call_llm
from main.chatgpt.prompts import SELLER_PROMPT, CUSTOMER_PROMPT
from main.chatgpt.state import ConversationState, GeneralState

def apply_sale(state: GeneralState, sale: dict):
    item_id = sale["item_id"]
    qty = sale["quantity"]
    state["inventory"][item_id]["stock"] -= qty
    state["cash_register"] += state["inventory"][item_id]["price"] * qty
    state["completed_transactions"].append(sale)

def seller_node(conversation_state: ConversationState, general_state, id) -> ConversationState:
    prompt = f"""{SELLER_PROMPT}\n\n
        Inventory: {json.dumps(general_state['inventory'])}\n
        Conversation: {conversation_state['messages']}
    """
    resp = call_llm(prompt, expect_json=True)

    items_text = []
    for sale in resp.get("berries_sold", []):
        item_id = sale["item_id"]
        qty = sale["quantity"]
        name = general_state["inventory"][item_id]["name"]
        items_text.append(f"{qty} x {name}")

    if items_text:
        total = sum(general_state["inventory"][sale["item_id"]]["price"] *
                    sale["quantity"] for sale in resp["berries_sold"])
        response_text = f"Sale complete: {', '.join(items_text)}. Total: ${total:.2f}."
    else:
        response_text = resp["response"]
        for item_id, info in general_state["inventory"].items():
            response_text = response_text.replace(item_id, info["name"])

    msg = "Seller: " + response_text
    conversation_state["messages"].append(HumanMessage(content=msg))
    print(msg)

    for sale in resp.get("berries_sold", []):
        apply_sale(general_state, sale)

    conversation_state["conversation_active"] = resp["conversation_should_continue"]
    conversation_state["conversation_turn"] += 1
    return conversation_state

def customer_node(conversation_state: ConversationState) -> ConversationState:
    prompt = f"{CUSTOMER_PROMPT}\n\nConversation: {conversation_state['messages']}"
    resp = call_llm(prompt)

    msg = "Customer: " + resp
    conversation_state["messages"].append(HumanMessage(content=msg))
    conversation_state["conversation_turn"] += 1
    print(msg)
    return conversation_state