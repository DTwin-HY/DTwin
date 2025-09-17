from langgraph.graph import StateGraph, START, END
from .state import init_cash_and_inventory_state, ConversationState
from .nodes import seller_node, customer_node
from .summary import print_summary

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