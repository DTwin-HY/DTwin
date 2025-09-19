import json
from langchain_core.messages import HumanMessage
from .llm_utils import call_llm
from .prompts import SELLER_PROMPT, CUSTOMER_PROMPT
from .services.mutations import apply_sale, set_raining
from .state import ConversationState

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
    general_state["conversations"][id] = conversation_state["messages"]
    print(f"(conversation {id}) {msg}")

    for sale in resp.get("berries_sold", []):
        apply_sale(general_state, sale)

    conversation_state["conversation_active"] = resp["conversation_should_continue"]
    conversation_state["conversation_turn"] += 1
    return conversation_state

def customer_node(conversation_state: ConversationState, general_state, id) -> ConversationState:
    is_raining = set_raining(general_state)
    prompt = f"{CUSTOMER_PROMPT}\n\nConversation: {conversation_state['messages']} \n\nIs it raining? {is_raining}"
    resp = call_llm(prompt)

    msg = "Customer: " + resp
    conversation_state["messages"].append(HumanMessage(content=msg))
    conversation_state["conversation_turn"] += 1
    print(f"(conversation {id}) {msg}")
    return conversation_state