import uuid
import threading
from datetime import datetime, timedelta
from .services.mutations import set_raining
from .state import ConversationState, init_conversation_state, init_general_state
from .nodes import seller_node, customer_node
from langgraph.graph import StateGraph, START, END

"""
currently unnecessary functions are stored here jujstin case
"""
conversation_logs = {}
lock = threading.Lock()

def log_conversation_message(conversation_id, agent_type, message, metadata=None):
    """Log a conversation message with thread safety"""
    with lock:
        if conversation_id not in conversation_logs:
            conversation_logs[conversation_id] = []
        
        log_entry = {
            "agent": agent_type,
            "type": "assistant" if agent_type in ["seller", "customer"] else "system",
            "content": message,
            "timestamp": datetime.now().isoformat(),
            "conversation_id": conversation_id
        }
        
        if metadata:
            log_entry.update(metadata)
            
        conversation_logs[conversation_id].append(log_entry)

def generate_sales_schedule(simulation_date, opening_hour=12, closing_hour=16):
    """Generate realistic timestamps for sales throughout the day"""
    import random
    
    peak_hours = [13, 14, 15]
    
    # Generate number of sales for the day
    base_sales = random.randint(4, 7)
    
    # Add extra sales during peak hours
    if any(hour in peak_hours for hour in range(opening_hour, closing_hour)):
        peak_bonus = random.randint(0, 3)
        total_sales = base_sales + peak_bonus
    else:
        total_sales = base_sales
    
    # Generate timestamps
    timestamps = []
    operating_minutes = (closing_hour - opening_hour) * 60
    
    for i in range(total_sales):
        # Distribute sales throughout the day
        if random.random() < 0.6 and len(peak_hours) > 0:  # 60% chance during peak
            peak_hour = random.choice(peak_hours)
            hour = peak_hour
            minute = random.randint(0, 59)
        else:
            random_minute = random.randint(0, operating_minutes - 1)
            hour = opening_hour + (random_minute // 60)
            minute = random_minute % 60
        
        sale_time = simulation_date.replace(hour=hour, minute=minute, second=random.randint(0, 59))
        timestamps.append(sale_time)
    
    timestamps.sort()
    
    # Make sure there's minimum gap between sales (5mins now)
    adjusted_timestamps = []
    for i, timestamp in enumerate(timestamps):
        if i == 0:
            adjusted_timestamps.append(timestamp)
        else:
            prev_time = adjusted_timestamps[-1]
            time_diff = (timestamp - prev_time).total_seconds() / 60
            
            if time_diff < 5:  # If less than 5 minutes apart, add 5-30min gap
                gap_minutes = random.randint(5, 30)
                new_time = prev_time + timedelta(minutes=gap_minutes)
                
                # Make sure sales times don't go past closing time
                max_time = simulation_date.replace(hour=closing_hour-1, minute=59)
                if new_time <= max_time:
                    adjusted_timestamps.append(new_time)
                else:
                    adjusted_timestamps.append(max_time)
            else:
                adjusted_timestamps.append(timestamp)
    
    return adjusted_timestamps

def simulate_single_sale(general_state, simulation_date, sale_timestamp, conversation_id, global_conversation_id):
    print(f"Starting AI simulation for sale at {sale_timestamp.strftime('%H:%M')}")
    
    log_conversation_message(
        global_conversation_id,
        "system",
        f"{sale_timestamp.strftime('%H:%M')} - Customer arrives at the berry stand..."
    )
    
    try:
        set_raining_result = set_raining(general_state)
        weather_msg = "It's raining" if set_raining_result else "☀️ Nice weather"
        log_conversation_message(global_conversation_id, "system", weather_msg)
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
            
            if updated_state.get("messages") and len(updated_state["messages"]) > 0:
                last_message = updated_state["messages"][-1]
                if hasattr(last_message, 'content'):
                    seller_msg = last_message.content
                    if seller_msg.startswith("Seller: "):
                        seller_msg = seller_msg[8:]
                    
                    log_conversation_message(
                        global_conversation_id,
                        "seller", 
                        seller_msg
                    )
            
            return updated_state
        except Exception as e:
            print(f"ERROR in seller_node: {e}")
            log_conversation_message(
                global_conversation_id,
                "system", 
                f"Error in seller interaction: {str(e)}"
            )
            state["conversation_active"] = False
            return state
    
    def logged_customer_node(state):
        try:
            updated_state = customer_node(state, general_state, conversation_id)
            
            if updated_state.get("messages") and len(updated_state["messages"]) > 0:
                last_message = updated_state["messages"][-1]
                if hasattr(last_message, 'content'):
                    customer_msg = last_message.content
                    if customer_msg.startswith("Customer: "):
                        customer_msg = customer_msg[9:]
                    
                    log_conversation_message(
                        global_conversation_id,
                        "customer", 
                        customer_msg
                    )
            
            return updated_state
        except Exception as e:
            print(f"ERROR in customer_node: {e}")
            log_conversation_message(
                global_conversation_id,
                "system", 
                f"Error in customer interaction: {str(e)}"
            )
            state["conversation_active"] = False
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
    
    initial_state = init_conversation_state()
    
    try:
        final_state = app.invoke(initial_state)
        
        if not final_state.get("conversation_active", True):
            log_conversation_message(
                global_conversation_id,
                "system", 
                "Conversation ended"
            )
        elif final_state.get("conversation_turn", 0) >= final_state.get("max_turns", 6):
            log_conversation_message(
                global_conversation_id,
                "system", 
                "Conversation ended (max turns reached)"
            )
            
    except Exception as e:
        print(f"ERROR executing conversation graph: {e}")
        log_conversation_message(
            global_conversation_id,
            "system", 
            f"Error executing conversation: {str(e)}"
        )
    
    final_cash = general_state["cash_register"]
    final_transactions_count = len(general_state.get("completed_transactions", []))
    
    sales_made = []
    
    if final_cash > initial_cash:
        cash_increase = final_cash - initial_cash
        log_conversation_message(
            global_conversation_id,
            "system",
            f"Cash register increased by €{cash_increase:.2f}"
        )
    
    if final_transactions_count > initial_transactions_count:
        new_transactions = general_state["completed_transactions"][initial_transactions_count:]
        
        for transaction in new_transactions:
            transaction["timestamp"] = sale_timestamp
            
            item_name = general_state["inventory"][transaction["item_id"]]["name"]
            
            sales_made.append({
                "transaction_id": transaction["transaction_id"],
                "item_id": transaction["item_id"],
                "item_name": item_name,
                "quantity": transaction["quantity"],
                "amount": transaction["amount"],
                "timestamp": sale_timestamp.isoformat()
            })
            
            log_conversation_message(
                global_conversation_id,
                "system",
                f"💰 Sale recorded: {transaction['quantity']}x {item_name} for €{transaction['amount']:.2f}"
            )
    
    if not sales_made:
        log_conversation_message(
            global_conversation_id,
            "system",
            "🚶 Customer leaves without purchasing"
        )
    
    print(f"Completed AI simulation for {sale_timestamp.strftime('%H:%M')}, sales: {len(sales_made)}")
    return sales_made

def run_full_day_simulation(num_conversations=None, simulation_date=None):
    """Run a full day simulation using LangGraph StateGraph for each customer interaction"""
    global conversation_logs
    
    if simulation_date is None:
        simulation_date = datetime.now()
    
    global_conversation_id = str(uuid.uuid4())
    
    with lock:
        conversation_logs[global_conversation_id] = []
    
    general_state = init_general_state(7)
    
    log_conversation_message(
        global_conversation_id,
        "system",
        f"Berry Stand opens for {simulation_date.strftime('%A, %B %d, %Y')}"
    )
    
    log_conversation_message(
        global_conversation_id,
        "system",
        f"Opening hours: 12:00 PM - 4:00 PM"
    )
    
    inventory_msg = "Starting inventory:\n"
    for item in general_state["inventory"].values():
        inventory_msg += f"   • {item['name']}: {item['stock']} boxes at €{item['price']:.2f} each\n"
    
    log_conversation_message(
        global_conversation_id,
        "system",
        inventory_msg.strip()
    )
    
    sale_timestamps = generate_sales_schedule(simulation_date)
    
    all_simulated_sales = []
    for i, timestamp in enumerate(sale_timestamps):
        log_conversation_message(
            global_conversation_id,
            "system",
            f"Running AI simulation {i+1}/{len(sale_timestamps)}..."
        )
        
        sales_from_interaction = simulate_single_sale(
            general_state, 
            simulation_date, 
            timestamp, 
            i, 
            global_conversation_id
        )
        
        all_simulated_sales.extend(sales_from_interaction)
        
        import time
        time.sleep(1)
    
    total_revenue = sum(sale["amount"] for sale in all_simulated_sales)
    items_sold = sum(sale["quantity"] for sale in all_simulated_sales)
    
    log_conversation_message(
        global_conversation_id,
        "system",
        f"End of day summary:"
    )
    
    log_conversation_message(
        global_conversation_id,
        "system",
        f"Total sales: {len(all_simulated_sales)} transactions, {items_sold} items sold"
    )
    
    log_conversation_message(
        global_conversation_id,
        "system",
        f"Total revenue: €{total_revenue:.2f}"
    )
    
    remaining_inventory = sum(item["stock"] for item in general_state["inventory"].values())
    log_conversation_message(
        global_conversation_id,
        "system",
        f"Remaining inventory: {remaining_inventory} boxes"
    )
    
    with lock:
        conversation_log = conversation_logs.get(global_conversation_id, [])
        # Clean up to prevent memory leaks
        if global_conversation_id in conversation_logs:
            del conversation_logs[global_conversation_id]
    
    return conversation_log, all_simulated_sales