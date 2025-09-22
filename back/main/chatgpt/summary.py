from .state import GeneralState
import datetime

def print_summary(state: GeneralState):
    print("\n📋 SALES SUMMARY")
    print("=" * 40)
    print(f"💰 Final cash register: €{state['cash_register']:.2f}")
    print("📦 FINAL INVENTORY:")
    for i in state["inventory"].values():
        print(f"   - {i['name']}: {i['stock']} in stock at €{i['price']:.2f} each")
    print("Conversations:")
    for i in range(len(state["conversations"])):
        print(f"--- Conversation {i} ---")
        for msg in state["conversations"][i]:
            print(msg.content)
        print("-" * 20)
    print("\n✅ Sales completed!")

"""
convert GeneralState to a JSON-serializable dict
"""
def general_state_to_jsonable(state):
    def serialize_message(msg):
        # Handles HumanMessage or similar objects
        return getattr(msg, "content", str(msg))

    def serialize_transaction(tx):
        tx_copy = dict(tx)
        if isinstance(tx_copy.get("timestamp"), datetime.datetime):
            tx_copy["timestamp"] = tx_copy["timestamp"].isoformat()
        return tx_copy

    return {
        "conversations": [
            [serialize_message(msg) for msg in conv]
            for conv in state.get("conversations", [])
        ],
        "cash_register": state.get("cash_register"),
        "inventory": state.get("inventory"),
        "sales": [
            serialize_transaction(tx)
            for tx in state.get("completed_transactions", [])
        ],
        "is_raining": state.get("is_raining")
    }