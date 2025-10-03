import uuid
import threading
from datetime import datetime, timedelta
from .services.mutations import set_raining
from .state import ConversationState, init_conversation_state, init_general_state
from .nodes import seller_node, customer_node
from langgraph.graph import StateGraph, START, END

conversation_logs = {}
lock = threading.Lock()

def log_conversation_message(conversation_id, agent_type, message, metadata=None, timestamp=None):
    """Log a conversation message with thread safety"""
    with lock:
        if conversation_id not in conversation_logs:
            conversation_logs[conversation_id] = []
        
        log_entry = {
            "agent": agent_type,
            "type": "assistant" if agent_type in ["seller", "customer"] else "system",
            "content": message,
            "timestamp": (timestamp or datetime.now()).isoformat(),
            "conversation_id": conversation_id
        }
        
        if metadata:
            log_entry.update(metadata)
            
        conversation_logs[conversation_id].append(log_entry)

def generate_sales_schedule(simulation_date, opening_hour=12, closing_hour=16):
    """Generate realistic timestamps for sales throughout the day"""
    import random

    simulation_date = simulation_date.replace(hour=0, minute=0, second=0, microsecond=0)
    
    peak_hours = [13, 14, 15]
    
    # Generate number of sales for the day
    base_sales = random.randint(4, 7)
    peak_bonus = random.randint(0, 3)
    total_sales = base_sales + peak_bonus
    
    timestamps = []
    operating_minutes = (closing_hour - opening_hour) * 60
    
    for i in range(total_sales):
        if random.random() < 0.6:
            hour = random.choice(peak_hours)
            minute = random.randint(0, 59)
        else:
            random_minute = random.randint(0, operating_minutes - 1)
            hour = opening_hour + (random_minute // 60)
            minute = random_minute % 60
        
        sale_time = simulation_date + timedelta(hours=hour, minutes=minute, seconds=random.randint(0, 59))
        timestamps.append(sale_time)
    
    timestamps.sort()
    
    # Ensure minimum 5-minute gap
    adjusted_timestamps = []
    for i, ts in enumerate(timestamps):
        if i == 0:
            adjusted_timestamps.append(ts)
        else:
            prev_time = adjusted_timestamps[-1]
            diff_min = (ts - prev_time).total_seconds() / 60
            if diff_min < 5:
                gap = timedelta(minutes=random.randint(5, 30))
                new_ts = prev_time + gap
                max_time = simulation_date.replace(hour=closing_hour-1, minute=59)
                adjusted_timestamps.append(min(new_ts, max_time))
            else:
                adjusted_timestamps.append(ts)
    
    return adjusted_timestamps

def simulate_single_sale(general_state, simulation_date, sale_timestamp, conversation_id, global_conversation_id):
    """Simulate a single customer interaction and return the sales made"""
    sale_timestamp = sale_timestamp.replace(
        year=simulation_date.year,
        month=simulation_date.month,
        day=simulation_date.day
    )
    print(f"Starting AI simulation for sale at {sale_timestamp.strftime('%H:%M')}")

    log_conversation_message(global_conversation_id, "system",
                             f"{sale_timestamp.strftime('%H:%M')} - Customer arrives at the berry stand...",
                             timestamp=sale_timestamp)
    
    try:
        set_raining_result = set_raining(general_state)
        weather_msg = "It's raining" if set_raining_result else "☀️ Nice weather"
        log_conversation_message(global_conversation_id, "system", weather_msg, timestamp=sale_timestamp)
    except Exception as e:
        print(f"WARNING: Could not set weather: {e}")
        general_state["is_raining"] = False

    initial_cash = general_state["cash_register"]
    initial_transactions_count = len(general_state.get("completed_transactions", []))
    if "conversations" not in general_state:
        general_state["conversations"] = {}

    graph = StateGraph(ConversationState)

    def logged_seller_node(state):
        try:
            updated_state = seller_node(state, general_state, conversation_id)
            if updated_state.get("messages"):
                for msg in updated_state["messages"]:
                    if hasattr(msg, "content"):
                        content = msg.content
                        if content.startswith("Seller: "):
                            content = content[8:]
                        log_conversation_message(global_conversation_id, "seller", content, timestamp=sale_timestamp)
            return updated_state
        except Exception as e:
            state["conversation_active"] = False
            log_conversation_message(global_conversation_id, "system", f"Error in seller_node: {e}", timestamp=sale_timestamp)
            return state

    def logged_customer_node(state):
        try:
            updated_state = customer_node(state, general_state, conversation_id)
            if updated_state.get("messages"):
                for msg in updated_state["messages"]:
                    if hasattr(msg, "content"):
                        content = msg.content
                        if content.startswith("Customer: "):
                            content = content[9:]
                        log_conversation_message(global_conversation_id, "customer", content, timestamp=sale_timestamp)
            return updated_state
        except Exception as e:
            state["conversation_active"] = False
            log_conversation_message(global_conversation_id, "system", f"Error in customer_node: {e}", timestamp=sale_timestamp)
            return state

    graph.add_node("seller", logged_seller_node)
    graph.add_node("customer", logged_customer_node)
    graph.add_edge(START, "seller")
    graph.add_conditional_edges(
        "seller",
        lambda s: END if not s.get("conversation_active", True) or s.get("conversation_turn", 0) >= s.get("max_turns", 6) else "customer"
    )
    graph.add_conditional_edges(
        "customer",
        lambda s: END if not s.get("conversation_active", True) or s.get("conversation_turn", 0) >= s.get("max_turns", 6) else "seller"
    )

    app = graph.compile()
    final_state = app.invoke(init_conversation_state())

    # Collect sales
    sales_made = []
    new_transactions = general_state.get("completed_transactions", [])[initial_transactions_count:]
    for tx in new_transactions:
        tx["timestamp"] = sale_timestamp
        item_name_str = general_state["inventory"][tx["item_id"]]["name"]
        sales_made.append({
            "transaction_id": tx["transaction_id"],
            "item_id": tx["item_id"],
            "item_name": item_name_str,
            "quantity": tx["quantity"],
            "amount": tx["amount"],
            "timestamp": sale_timestamp.isoformat()
        })
        log_conversation_message(global_conversation_id, "system",
                                 f"💰 Sale recorded: {tx['quantity']}x {item_name_str} for €{tx['amount']:.2f}",
                                 timestamp=sale_timestamp)

    if not sales_made:
        log_conversation_message(global_conversation_id, "system", "🚶 Customer leaves without purchasing", timestamp=sale_timestamp)

    print(f"Completed AI simulation for {sale_timestamp.strftime('%H:%M')}, sales: {len(sales_made)}")
    return sales_made

def run_full_day_simulation(num_conversations=None, simulation_date=None):
    """Run a full day simulation with multiple customer interactions"""
    global conversation_logs
    if simulation_date is None:
        raise ValueError("simulation_date must be provided")

    global_conversation_id = str(uuid.uuid4())
    with lock:
        conversation_logs[global_conversation_id] = []

    general_state = init_general_state(7)

    log_conversation_message(global_conversation_id, "system",
                             f"Berry Stand opens for {simulation_date.strftime('%A, %B %d, %Y')}",
                             timestamp=simulation_date)
    log_conversation_message(global_conversation_id, "system",
                             f"Opening hours: 12:00 PM - 4:00 PM",
                             timestamp=simulation_date)

    inventory_msg = "Starting inventory:\n"
    for item in general_state["inventory"].values():
        inventory_msg += f"   • {item['name']}: {item['stock']} boxes at €{item['price']:.2f} each\n"
    log_conversation_message(global_conversation_id, "system", inventory_msg.strip())

    sale_timestamps = generate_sales_schedule(simulation_date)
    all_simulated_sales = []

    for i, ts in enumerate(sale_timestamps):
        log_conversation_message(global_conversation_id, "system", f"Running AI simulation {i+1}/{len(sale_timestamps)}...")
        sales = simulate_single_sale(general_state, simulation_date, ts, i, global_conversation_id)
        all_simulated_sales.extend(sales)
        import time; time.sleep(1)

    total_revenue = sum(sale["amount"] for sale in all_simulated_sales)
    items_sold = sum(sale["quantity"] for sale in all_simulated_sales)
    log_conversation_message(global_conversation_id, "system", f"End of day summary:")
    log_conversation_message(global_conversation_id, "system", f"Total sales: {len(all_simulated_sales)} transactions, {items_sold} items sold")
    log_conversation_message(global_conversation_id, "system", f"Total revenue: €{total_revenue:.2f}")
    remaining_inventory = sum(item["stock"] for item in general_state["inventory"].values())
    log_conversation_message(global_conversation_id, "system", f"Remaining inventory: {remaining_inventory} boxes")

    with lock:
        conversation_log = conversation_logs.pop(global_conversation_id, [])

    return conversation_log, all_simulated_sales