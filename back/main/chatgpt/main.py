import threading
from datetime import datetime

from langgraph.graph import END, START, StateGraph

from .nodes import customer_node, seller_node
from .state import ConversationState, init_conversation_state, init_general_state
from .summary import general_state_to_jsonable, print_summary


def run_conversation(general_state, conversation_id, simulation_date):
    """
    for running a single conversation between a seller and a customer
    initializes its own conversation-specific state, runs the conversation and updates the general state
    """
    print(f"Starting conversation {conversation_id} on {simulation_date.date()}...\n")

    graph = StateGraph(ConversationState)
    graph.add_node("seller", lambda state: seller_node(state, general_state, conversation_id))
    graph.add_node("customer", lambda state: customer_node(state, general_state, conversation_id))

    graph.add_edge(START, "seller")
    graph.add_conditional_edges(
        "seller",
        lambda s: (
            END
            if not s["conversation_active"] or s["conversation_turn"] >= s["max_turns"]
            else "customer"
        ),
    )
    graph.add_edge("customer", "seller")

    app = graph.compile()
    state = init_conversation_state()
    state = app.invoke(state)
    print(f"\nConversation {conversation_id} ended.")


def run_multiple_conversations(num_conversations=3, simulation_date=None, is_raining=False):
    """
    for running multiple conversations in parallel threads
    initializes the general state and starts multiple conversation threads
    """
    if simulation_date is None:
        simulation_date = datetime.now()

    general_state = init_general_state(num_conversations)
    general_state["is_raining"] = is_raining

    print(f"\n📊 INITIAL BUSINESS STATE ({simulation_date.date()}):")
    print(f"💰 Cash Register: €{general_state['cash_register']:.2f}")
    print("📦 Inventory:")
    for i in general_state["inventory"].values():
        print(f"   - {i['name']}: {i['stock']} in stock at €{i['price']:.2f} each")
    print("\n🎬 STARTING CONVERSATIONS...")

    threads = []
    for conv_id in range(num_conversations):
        t = threading.Thread(
            target=run_conversation, args=(general_state, conv_id, simulation_date)
        )
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print_summary(general_state)
    result = general_state_to_jsonable(general_state)
    return result


if __name__ == "__main__":
    run_multiple_conversations(3)
