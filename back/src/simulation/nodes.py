import json
import random
import uuid
<<<<<<< HEAD:back/main/chatgpt/nodes.py

=======
from sqlalchemy.sql import text
>>>>>>> f31294b (Refactor the backend and removed useless imports):back/main/simulation/nodes.py
from langchain_core.messages import HumanMessage

from .llm_utils import call_llm
<<<<<<< HEAD:back/main/chatgpt/nodes.py
from .prompts import CUSTOMER_PROMPT, SELLER_PROMPT
from .services.mutations import apply_sale
=======
from .prompts import SELLER_PROMPT, CUSTOMER_PROMPT
from ..services.mutations import apply_sale
>>>>>>> f31294b (Refactor the backend and removed useless imports):back/main/simulation/nodes.py
from .state import ConversationState


def seller_node(conversation_state: ConversationState, general_state, id) -> ConversationState:
    """
    Seller agent node in the conversation graph
    Calls the LLM with the given prompt and current state
    Updates the transactions to the general state
    Adds messages to the conversation state
    """
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
        total = sum(
            general_state["inventory"][sale["item_id"]]["price"] * sale["quantity"]
            for sale in resp["berries_sold"]
        )
        response_text = f"Sale complete: {', '.join(items_text)}. Total: ${total:.2f}."
    else:
        response_text = resp["response"]
        for item_id, info in general_state["inventory"].items():
            response_text = response_text.replace(item_id, info["name"])

    msg = "Seller: " + response_text
    conversation_state["messages"].append(HumanMessage(content=msg))
    general_state["conversations"][id] = conversation_state["messages"]
    print(f"(conversation {id}) {msg}")

    transaction_id = str(uuid.uuid4())

    for sale in resp.get("berries_sold", []):
        apply_sale(general_state, sale, transaction_id)

    conversation_state["conversation_active"] = resp["conversation_should_continue"]
    conversation_state["conversation_turn"] += 1
    return conversation_state


def customer_node(conversation_state: ConversationState, general_state, id) -> ConversationState:
    """
    Customer agent node in the conversation graph
    Calls the LLM with the given prompt and current state
    Adds messages to the conversation state
    """
    is_raining = general_state.get("is_raining", False)

    if is_raining and random.random() > 0.3:
        rain_context = "\n\nIt's raining. You've decided not to buy berries because of weather."
        prompt = f"{CUSTOMER_PROMPT}{rain_context}\n\nConversation:{conversation_state['messages']} \n\nIs it raining? {is_raining}"
    else:
        prompt = f"{CUSTOMER_PROMPT}\n\nConversation: {conversation_state['messages']} \n\nIs it raining? {is_raining}"

    print("is it raining?", is_raining)
    resp = call_llm(prompt)

    msg = "Customer: " + resp
    conversation_state["messages"].append(HumanMessage(content=msg))
    conversation_state["conversation_turn"] += 1
    print(f"(conversation {id}) {msg}")
    return conversation_state
