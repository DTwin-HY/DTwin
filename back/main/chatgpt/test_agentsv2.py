from typing import TypedDict, Annotated, Dict, Any, Optional, List, Literal
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
import os, json
from dotenv import load_dotenv

class ConversationState(TypedDict):
    messages: Annotated[list, add_messages]
    cash_register: float
    inventory: Dict[str, Dict[str, Any]]
    conversation_turn: int
    conversation_active: bool
    max_turns: int
    completed_transactions: List[Dict[str, Any]]

def init_cash_and_inventory_state() -> ConversationState:
    return {
        "messages": [],
        "cash_register": 400.0,
        "inventory": {
            "strawberries_small": {"stock": 20, "price": 3.0, "name": "Small box"},
            "strawberries_medium": {"stock": 15, "price": 5.0, "name": "Medium box"},
        },
        "conversation_turn": 0,
        "conversation_active": True,
        "max_turns": 8,
        "completed_transactions": []
    }

load_dotenv()
SELECTED_MODEL = "gpt-5-nano"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(model=SELECTED_MODEL, api_key=OPENAI_API_KEY)

def seller_node(state: ConversationState) -> ConversationState:
    prompt = f"""
    You are a helpful seller at a berry stand. Your goal is to complete transactions efficiently.
    Current situation:
    Inventory: {json.dumps(state['inventory'])}
    The ongoing conversation: {state['messages']}

    IMPORTANT TRANSACTION RULES:
    1. If customer has confirmed their order, payment method, and receipt preference, COMPLETE THE SALE
    2. If customer keeps repeating the same questions, politely finalize and wrap up
    3. If transaction details are all confirmed, execute the sale and end conversation
    4. Don't keep asking for more confirmations once everything is clear

    Analyze the customer's message:
    - If they're confirming an order → Process the sale and wrap up
    - If they're asking new questions → Answer helpfully
    - If they're repeating confirmations → Complete transaction
    - If order is fully specified → Execute sale

    Respond in JSON format:
    {{
        "response": "Your response to customer",
        "conversation_should_continue": true/false,
        "berries_sold": [
            {{"item_id": "strawberries_small", "quantity": 2}},
            {{"item_id": "strawberries_medium", "quantity": 0}}
        ]
    }}

    Change the conversation_should_continue to false if the transaction is complete or if the customer is leaving and
    update the berries_sold accordingly.
    """

    resp = llm.invoke([HumanMessage(content=prompt)])
    resp = json.loads(resp.content)
    msg = "Seller: " + resp["response"].strip()
    print(msg)
    state["messages"].append(HumanMessage(content=msg))

    if not resp["conversation_should_continue"]:
        state["conversation_active"] = False

        if resp.get("berries_sold"):
            for sale in resp["berries_sold"]:
                item_id = sale["item_id"]
                quantity = sale["quantity"]

                # Update inventory
                state["inventory"][item_id]["stock"] = state["inventory"][item_id]["stock"] - quantity

                # Add cash
                price = state["inventory"][item_id]["price"]
                state["cash_register"] = state["cash_register"] + price * quantity

    state["conversation_turn"] += 1
    return state

def customer_node(state: ConversationState) -> ConversationState:
    prompt = f"""
    You are a customer at a berry stand.
    Ongoing conversation: {state['messages']}

    IMPORTANT CUSTOMER BEHAVIOR:
        1. If seller confirms your order is complete/ready, say thank you and goodbye
        2. If you've asked the same question 2+ times, accept the seller's answer
        3. If transaction details are confirmed, express satisfaction and end conversation
        4. Don't keep repeating the same confirmation questions

        If seller seems to have completed your order or you've repeated questions too much,
        respond with thanks and goodbye. Otherwise, respond naturally but don't repeat
        the same questions you've already asked.

        Generate ONE natural customer response.
    """
    resp = llm.invoke([HumanMessage(content=prompt)])
    msg = "Customer: " + resp.content.strip()
    state["messages"].append(HumanMessage(content=msg))
    state["conversation_turn"] += 1
    print(msg)
    return state

def run_conversation():
    graph = StateGraph(ConversationState)

    graph.add_node("seller", seller_node)
    graph.add_node("customer", customer_node)

    graph.add_edge(START, "seller")
    graph.add_conditional_edges(
        "seller",
        lambda s: END if not s["conversation_active"] or s["conversation_turn"] >= s["max_turns"] else "customer"
    )
    graph.add_edge("customer", "seller")

    app = graph.compile()

    state = init_cash_and_inventory_state()

    print(f"\n📊 INITIAL BUSINESS STATE:")
    print(f"💰 Cash Register: €{state['cash_register']:.2f}")
    print(f"📦 Inventory:")
    for i in state["inventory"].items():
        print(f"   - {i[1]['name']}: {i[1]['stock']} in stock at €{i[1]['price']:.2f} each")
    print(f"\n🎬 STARTING CONVERSATION...")

    state=app.invoke(state)

    print("📋 CONVERSATION SUMMARY")
    print("=" * 60)
    print(f"🔄 Total turns: {state.get('conversation_turn', 0)}")
    print(f"💰 Final cash register: €{state.get('cash_register', 0):.2f}")

    print(f"\n📦 FINAL INVENTORY:")
    for i in state["inventory"].items():
        print(f"   - {i[1]['name']}: {i[1]['stock']} in stock at €{i[1]['price']:.2f} each")

    print("\n✅ Conversation completed!")

if __name__ == "__main__":
    run_conversation()
