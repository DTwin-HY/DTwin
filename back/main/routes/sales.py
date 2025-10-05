from datetime import datetime, timedelta

from flask import abort, jsonify, request
from flask_login import login_required
from sqlalchemy.sql import text

from main.chatgpt.main import run_multiple_conversations
from main.chatgpt.requests.req_weather import fetch_weather
from main.models import Sale
from main.utils.item_name import item_name

from ..index import app, db


@app.get("/api/sales")
@login_required
def get_sales():
    """
    fetch sales for a specific day (default today)
    body: { "date": "YYYY-MM-DD" }
    """
    date_str = request.args.get("date")
    if date_str:
        day = datetime.strptime(date_str, "%Y-%m-%d")
    else:
        day = datetime.now()

    day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = day_start + timedelta(days=1)

    sql = text(
        "SELECT transaction_id, item_id, quantity, amount, timestamp FROM sales "
        "WHERE timestamp >= :start AND timestamp < :end ORDER BY timestamp ASC"
    )
    result = db.session.execute(sql, {"start": day_start, "end": day_end})

    # format the result
    sales = [
        {
            "transaction_id": row["transaction_id"],
            "item_id": row["item_id"],
            "item_name": item_name(row["item_id"]) or row["item_id"],
            "quantity": row["quantity"],
            "amount": float(row["amount"]),
            "timestamp": row["timestamp"].isoformat(),
        }
        for row in result.mappings()
    ]
    return jsonify({"sales": sales})


@app.post("/api/simulate-sales")
@login_required
def simulate_sales():
    """
    simulate a full day of sales using AI conversations
    body: { "date": "YYYY-MM-DD" }
    """
    if not request.is_json:
        abort(400, description="Body must be JSON")

    data = request.get_json()
    date_str = data.get("date")
    lat = data.get("lat")
    lon = data.get("lon")

    if not date_str:
        return jsonify({"error": "Date is required"}), 400
    if lat is None or lon is None:
        return jsonify({"error": "Latitude and longitude are required"}), 400

    try:
        simulation_date = datetime.strptime(date_str, "%Y-%m-%d")
        print(f"Starting full day sales simulation for {simulation_date.date()}...")

        weather = fetch_weather(lat, lon, date_str)
        is_raining = weather.get("is_raining", False)
        result = run_multiple_conversations(
            10, simulation_date=simulation_date, is_raining=is_raining
        )

        simulated_sales = result.get("sales", [])

        for sale in simulated_sales:
            sale["item_name"] = item_name(sale.get("item_id")) or sale.get("item_id")
            original_time = datetime.fromisoformat(sale["timestamp"])
            simulated_timestamp = simulation_date.replace(
                hour=original_time.hour,
                minute=original_time.minute,
                second=original_time.second,
                microsecond=original_time.microsecond,
            )

            new_sale = Sale(
                transaction_id=sale["transaction_id"],
                item_id=sale["item_id"],
                quantity=sale["quantity"],
                amount=sale["amount"],
                timestamp=simulated_timestamp,
            )
            db.session.add(new_sale)

        db.session.commit()

        return jsonify(result)

    except ValueError as e:
        return jsonify({"error": f"Invalid date format: {str(e)}"}), 400
    except Exception as e:
        print(f"Error during simulation: {str(e)}")
        return jsonify({"error": f"Simulation failed: {str(e)}"}), 500
