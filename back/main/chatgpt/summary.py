from .state import GeneralState

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