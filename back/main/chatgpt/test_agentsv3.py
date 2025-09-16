from typing import TypedDict, Annotated, Dict, Any, List
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

SELLER_PROMPT = """
You are a berry stand seller. Your task is to handle sales quickly and clearly.

Rules:
- If the order is complete, finalize sale and end conversation.
- Avoid repeating confirmations.
- Always return valid JSON:
{
  "response": "...",
  "conversation_should_continue": true/false,
  "berries_sold": [{"item_id": "...", "quantity": N}]
}
"""

CUSTOMER_PROMPT = """
You are a berry stand customer.

Rules:
- If order is ready or repeated questions occur, thank and leave.
- Otherwise, ask naturally but without repetition.
Return only a natural customer response.
"""
#yhdistin seller_node ja customer_node LLM-kutsut samaan funktioon
def call_llm(prompt: str, expect_json: bool = False) -> Any:
    resp = llm.invoke([HumanMessage(content=prompt)])
    content = resp.content.strip()
    return json.loads(content) if expect_json else content

def apply_sale(state: ConversationState, sale: Dict[str, Any]):
    #myyntitapahtuman päivitys omaan funktioon
    item_id = sale["item_id"]
    qty = sale["quantity"]
    state["inventory"][item_id]["stock"] -= qty
    state["cash_register"] += state["inventory"][item_id]["price"] * qty
    state["completed_transactions"].append(sale)

def seller_node(state: ConversationState) -> ConversationState:
    #lyhyempi ja selkeämpi prompt
    prompt = f"{SELLER_PROMPT}\n\nInventory: {json.dumps(state['inventory'])}\nConversation: {state['messages']}"
    resp = call_llm(prompt, expect_json=True)

    #lisää viestin keskusteluun
    msg = "Seller: " + resp["response"]
    state["messages"].append(HumanMessage(content=msg))
    print(msg)

    #jos myyjä on valmis, päivitä tila ja varasto
    if not resp["conversation_should_continue"]:
        state["conversation_active"] = False
        for sale in resp.get("berries_sold", []):
            apply_sale(state, sale)
    state["conversation_turn"] += 1
    return state

def customer_node(state: ConversationState) -> ConversationState:
    #lyhyempi ja selkeä prompt asiakkaalle
    prompt = f"{CUSTOMER_PROMPT}\n\nConversation: {state['messages']}"
    resp = call_llm(prompt)

    msg = "Customer: " + resp
    state["messages"].append(HumanMessage(content=msg))
    state["conversation_turn"] += 1
    print(msg)
    return state

def print_summary(state: ConversationState):
    #yhteenvedolle oma funktio
    print("\n📋 CONVERSATION SUMMARY")
    print("=" * 40)
    print(f"🔄 Total turns: {state['conversation_turn']}")
    print(f"💰 Final cash register: €{state['cash_register']:.2f}")
    print(f"📦 FINAL INVENTORY:")
    for i in state["inventory"].values():
        print(f"   - {i['name']}: {i['stock']} in stock at €{i['price']:.2f} each")
    print("\n✅ Conversation completed!")

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
    for i in state["inventory"].values():
        print(f"   - {i['name']}: {i['stock']} in stock at €{i['price']:.2f} each")
    print(f"\n🎬 STARTING CONVERSATION...")

    state = app.invoke(state)
    print_summary(state)

if __name__ == "__main__":
    run_conversation()