from main.chatgpt.state import GeneralState

def print_summary(state: GeneralState):
    print("\n📋 SALES SUMMARY")
    print("=" * 40)
    print(f"💰 Final cash register: €{state['cash_register']:.2f}")
    print("📦 FINAL INVENTORY:")
    for i in state["inventory"].values():
        print(f"   - {i['name']}: {i['stock']} in stock at €{i['price']:.2f} each")
    print("\n✅ Sales completed!")