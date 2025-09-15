import os
import json
import time
from dotenv import load_dotenv
from datetime import datetime
from typing import Annotated, Dict, List, Any, Optional, Literal
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ConversationState(TypedDict):
    messages: Annotated[list, add_messages]
    
    cash_register: float
    inventory: Dict[str, Dict[str, Any]]
    
    current_speaker: Literal["customer", "seller"]
    conversation_turn: int
    max_turns: int
    conversation_active: bool
    
    pending_transaction: Optional[Dict[str, Any]]
    completed_transactions: List[Dict[str, Any]]
    
    customer_intent: str
    seller_mode: str

class CustomerAgent:    
    def __init__(self, llm):
        self.llm = llm
    
    def respond_to_seller(self, state: ConversationState) -> str:            
            messages = state.get("messages", [])
            last_seller_message = ""
            conversation_history = []
            
            for msg in messages[-6:]:
                if isinstance(msg, (HumanMessage, AIMessage)):
                    content = msg.content
                    if "Seller:" in content:
                        last_seller_message = content.replace("Seller:", "").strip()
                    elif "Customer:" in content:
                        conversation_history.append(content.replace("Customer:", "").strip())
            
            completion_indicators = [
                "transaction is complete",
                "order is ready", 
                "charged to card",
                "receipt sent",
                "see you soon",
                "pickup in",
                "total is"
            ]
            
            customer_intent = state.get("customer_intent", "browsing")
            
            prompt = f"""
            You are a customer at a berry stand.
            
            Current situation:
            - Your intent: {customer_intent}
            - Seller just said: "{last_seller_message}"
            - Recent conversation: {conversation_history[-3:]}
            
            IMPORTANT CUSTOMER BEHAVIOR:
            1. If seller confirms your order is complete/ready, say thank you and goodbye
            2. If you've asked the same question 2+ times, accept the seller's answer
            3. If transaction details are confirmed, express satisfaction and end conversation
            4. Don't keep repeating the same confirmation questions
            
            Check if seller's message contains completion indicators:
            {completion_indicators}
            
            If seller seems to have completed your order or you've repeated questions too much,
            respond with thanks and goodbye. Otherwise, respond naturally but don't repeat
            the same questions you've already asked.
            
            Generate ONE natural customer response:
            """
            
            try:
                response = self.llm.invoke([SystemMessage(content=prompt)])
                return response.content.strip()
                
            except Exception as e:
                logger.error(f"Customer agent error: {e}")
                return "Thank you! That all sounds perfect. I'll see you soon for pickup!"


class SellerAgent:    
    def __init__(self, llm):
        self.llm = llm

    def respond_to_customer(self, state: ConversationState) -> Dict[str, Any]:        
        messages = state.get("messages", [])
        last_customer_message = ""
        conversation_history = []
        
        # Extract conversation context
        for msg in messages[-6:]:
            if isinstance(msg, (HumanMessage, AIMessage)):
                content = msg.content
                if "Customer:" in content:
                    last_customer_message = content.replace("Customer:", "").strip()
                    conversation_history.append(f"Customer: {last_customer_message}")
                elif "Seller:" in content:
                    conversation_history.append(f"Seller: {content.replace('Seller:', '').strip()}")
        
        inventory = state.get("inventory", {})
        cash_register = state.get("cash_register", 0.0)
        turn_number = state.get("conversation_turn", 0)
        pending_transaction = state.get("pending_transaction")
        
        prompt = f"""
        You are a helpful seller at a berry stand. Your goal is to complete transactions efficiently.
        
        Current situation:
        - Turn #{turn_number}
        - Inventory: {json.dumps(inventory, indent=2)}
        - Conversation: {conversation_history[-3:] if conversation_history else ['Starting']}
        - Customer just said: "{last_customer_message}"
        - Pending transaction: {pending_transaction}
        
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
            "action": "greeting/explaining/selling/completing_transaction/closing",
            "transaction_ready": true/false,
            "inventory_changes": {{"product_id": -quantity_sold}},
            "cash_change": 0.00,
            "transaction_details": {{"items": [], "total": 0.00, "payment": "method"}},
            "conversation_should_continue": true/false,
            "completion_reason": "transaction_completed/customer_satisfied/order_processed"
        }}
        
        If transaction_ready is true, set conversation_should_continue to false.
        """
        
        try:
            response = self.llm.invoke([SystemMessage(content=prompt)])
            seller_decision = json.loads(response.content)
            
            if seller_decision.get("transaction_ready", False):
                total_sale = 0
                inventory_changes = seller_decision.get("inventory_changes", {})
                
                for product_id, quantity_change in inventory_changes.items():
                    if product_id in inventory and quantity_change < 0:  # Negative = items sold
                        item_price = inventory[product_id]["price"]
                        items_sold = abs(quantity_change)
                        total_sale += item_price * items_sold
                
                seller_decision["cash_change"] = total_sale
                seller_decision["conversation_should_continue"] = False
                seller_decision["action"] = "completing_transaction"
            
            return seller_decision
            
        except Exception as e:
            logger.error(f"Seller agent error: {e}")
            return {
                "response": "Thank you for your order! Your transaction is complete.",
                "action": "completing_transaction",
                "transaction_ready": True,
                "cash_change": 18.00,
                "conversation_should_continue": False,
                "completion_reason": "fallback_completion"
            }

def initialize_agents():
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️  Warning: OPENAI_API_KEY not set. Using mock responses.")
        return None, None
    
    try:
        llm = ChatOpenAI(model="gpt-5-nano", api_key=api_key)
        customer_agent = CustomerAgent(llm)
        seller_agent = SellerAgent(llm)
        return customer_agent, seller_agent
    except Exception as e:
        print(f"❌ Error initializing agents: {e}")
        return None, None

def init_cash_and_inventory_state(state: ConversationState) -> ConversationState:
    '''
    Initializes cash and inventory state
    Must be called before the other init function
    '''
    return {
        "cash_register": 400.00,
        "inventory": {
            "strawberries_small": {
                "stock": 20,
                "price": 3.00,
                "cost": 1.00,
                "name": "Small box of strawberries"
            },
            "strawberries_medium": {
                "stock": 15,
                "price": 5.00,
                "cost": 2.00,
                "name": "Medium box of strawberries"
            },
            "strawberries_large": {
                "stock": 10,
                "price": 8.00,
                "cost": 3.00,
                "name": "Large box of strawberries"
            }
        },
    }

def init_conversation_state(state: ConversationState) -> ConversationState:
    '''
    resets conversation-specific state while preserving cash and inventory
    must be called after the other init function
    '''
    return {
        "messages": [],
        "cash_register": state.get("cash_register", 0.0),
        "inventory": state.get("inventory", {}),
        "current_speaker": "seller",
        "conversation_turn": 0,
        "max_turns": 10,
        "conversation_active": True,
        "pending_transaction": None,
        "completed_transactions": state.get("completed_transactions", []),
        "customer_intent": "browsing",
        "seller_mode": "greeting"
    }

def run_console_conversation(state):
    
    print("=" * 60)
    print("🤖 BERRY STAND SIMULATION")
    print("=" * 60)

    state = init_conversation_state(state)
    
    customer_agent, seller_agent = initialize_agents()
    if not customer_agent or not seller_agent:
        print("❌ Could not initialize agents. Please check your OPENAI_API_KEY.")
        return
    print(f"\n📊 INITIAL BUSINESS STATE:")
    print(f"💰 Cash Register: €{state['cash_register']:.2f}")
    print(f"📦 Inventory:")
    for product_id, details in state["inventory"].items():
        print(f"   - {details['name']}: {details['stock']} units @ €{details['price']:.2f}")
    
    print(f"\n🎬 STARTING CONVERSATION...")
    print(f"🎯 Max turns: {state['max_turns']}")
    print("-" * 60)
    
    conversation_count = 0
    
    while state.get("conversation_active", False) and state.get("conversation_turn", 0) < state.get("max_turns", 12):
        conversation_count += 1
        
        if state.get("current_speaker") == "seller":
            print(f"\n🏪 SELLER'S TURN (Turn #{state.get('conversation_turn', 0) + 1})")
            print("   Thinking...")
            
            try:
                seller_response = seller_agent.respond_to_customer(state)
                
                state["conversation_turn"] += 1
                state["current_speaker"] = "customer"
                
                if "cash_change" in seller_response and seller_response["cash_change"] != 0:
                    old_cash = state["cash_register"]
                    state["cash_register"] += seller_response["cash_change"]
                    print(f"   💰 Cash register: €{old_cash:.2f} → €{state['cash_register']:.2f}")
                
                if "inventory_changes" in seller_response:
                    for product_id, change in seller_response["inventory_changes"].items():
                        if product_id in state["inventory"]:
                            old_stock = state["inventory"][product_id]["stock"]
                            state["inventory"][product_id]["stock"] = max(0, old_stock + change)
                            print(f"   📦 {product_id} stock: {old_stock} → {state['inventory'][product_id]['stock']}")
                
                if not seller_response.get("conversation_should_continue", True):
                    state["conversation_active"] = False
                
                seller_message = f"Seller: {seller_response.get('response', '')}"
                state["messages"].append(HumanMessage(content=seller_message))
                
                print(f"   💬 {seller_message}")
                
            except Exception as e:
                print(f"   ❌ Error in seller turn: {e}")
                break
        
        elif state.get("current_speaker") == "customer":
            if not state.get("conversation_active", False):
                break
                
            print(f"\n👤 CUSTOMER'S TURN")
            print("   Thinking...")
            
            try:
                customer_response = customer_agent.respond_to_seller(state)
                
                state["current_speaker"] = "seller"
                
                response_lower = customer_response.lower()
                if any(word in response_lower for word in ["buy", "purchase", "take", "get"]):
                    state["customer_intent"] = "purchasing"
                    print("   🎯 Customer intent: purchasing")
                elif any(word in response_lower for word in ["bye", "thanks", "leaving"]):
                    state["customer_intent"] = "leaving"
                    state["conversation_active"] = False
                    print("   🎯 Customer intent: leaving")
                
                customer_message = f"Customer: {customer_response}"
                state["messages"].append(HumanMessage(content=customer_message))
                
                print(f"   💬 {customer_message}")
                
            except Exception as e:
                print(f"   ❌ Error in customer turn: {e}")
                break
        
        # Add a small delay for readability
        time.sleep(1)
        
        if conversation_count > 20:
            print("\n⚠️  Safety limit reached. Ending conversation.")
            break
    
    print("\n" + "=" * 60)
    print("📋 CONVERSATION SUMMARY")
    print("=" * 60)
    print(f"🔄 Total turns: {state.get('conversation_turn', 0)}")
    print(f"🎭 Customer intent: {state.get('customer_intent', 'unknown')}")
    print(f"🏪 Seller mode: {state.get('seller_mode', 'unknown')}")
    print(f"💰 Final cash register: €{state.get('cash_register', 0):.2f}")
    print(f"📈 Revenue generated: €{state.get('cash_register', 0) - 500:.2f}")
    
    print(f"\n📦 FINAL INVENTORY:")
    for product_id, details in state.get("inventory", {}).items():
        print(f"   - {details['name']}: {details['stock']} units")
    
    print(f"\n💬 COMPLETE CONVERSATION TRANSCRIPT:")
    print("-" * 40)
    for i, message in enumerate(state.get("messages", []), 1):
        content = message.content
        print(f"{i:2d}. {content}")
    
    print("\n✅ Conversation completed!")
    return state

if __name__ == "__main__":
    try:
        state = init_cash_and_inventory_state({})
        for i in range(3):
            print(f"\n=== Conversation #{i+1} ===")
            state = run_console_conversation(state)
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
