from main.chatgpt.state import ConversationState

def print_summary(state: ConversationState):
    print("\n📋 CONVERSATION SUMMARY")
    print("=" * 40)
    print(f"🔄 Total turns: {state['conversation_turn']}")
    print(f"💰 Final cash register: €{state['cash_register']:.2f}")
    print("📦 FINAL INVENTORY:")
    for i in state["inventory"].values():
        print(f"   - {i['name']}: {i['stock']} in stock at €{i['price']:.2f} each")
    print("\n✅ Conversation completed!")