from langgraph.graph import StateGraph, START, END
import threading
from .state import ConversationState, init_conversation_state, init_general_state
from .nodes import seller_node, customer_node
from .summary import print_summary, general_state_to_jsonable

def run_conversation(general_state, conversation_id):
    """
    for running a single conversation between a seller and a customer
    initializes its own conversation-specific state, runs the conversation and updates the general state
    """
    print(f"Starting conversation {conversation_id}...\n")
    graph = StateGraph(ConversationState)
    graph.add_node("seller", lambda state: seller_node(state, general_state, conversation_id))
    graph.add_node("customer", lambda state: customer_node(state, general_state, conversation_id))
    graph.add_edge(START, "seller")
    graph.add_conditional_edges(
        "seller",
        lambda s: END if not s["conversation_active"] or s["conversation_turn"] >= s["max_turns"] else "customer"
    )
    graph.add_edge("customer", "seller")
    app = graph.compile()

    state = init_conversation_state()
    state = app.invoke(state)
    print(f"\nConversation {conversation_id} ended.")

def run_multiple_conversations(num_conversations=3):
    """
    for running multiple conversations in parallel threads
    initializes the general state and starts multiple conversation threads
    """
    general_state = init_general_state(num_conversations)

    print(f"\n📊 INITIAL BUSINESS STATE:")
    print(f"💰 Cash Register: €{general_state['cash_register']:.2f}")
    print(f"📦 Inventory:")
    for i in general_state["inventory"].values():
        print(f"   - {i['name']}: {i['stock']} in stock at €{i['price']:.2f} each")
    print(f"\n🎬 STARTING CONVERSATION...")

    threads = []
    for conv_id in range(num_conversations):
        t = threading.Thread(target=run_conversation, args=(general_state, conv_id))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print_summary(general_state)
    result = general_state_to_jsonable(general_state)
    return result

if __name__ == "__main__":
    run_multiple_conversations(3)
