from flask import jsonify, request
from sqlalchemy import text
from ..index import app
from ..extensions import db

@app.get("/api/sales-data")
def get_sales_data():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    if not start_date or not end_date:
        return jsonify({"error": "start_date and end_date are required"}), 400

    # Using transaction id as customers bc no customer_id yet in db
    query = text("""
        SELECT
            COALESCE(SUM(amount), 0) AS revenue,
            COUNT(DISTINCT transaction_id) AS customers,
            COALESCE(SUM(quantity), 0) AS total_units
        FROM sales
        WHERE timestamp BETWEEN :start AND :end;
    """)

    try:
        with db.engine.connect() as conn:
            result = conn.execute(query, {"start": start_date, "end": end_date})
            row = result.fetchone()
            data = dict(row._mapping)

            # Optional: rename keys to match your React component
            return jsonify({
                "revenue": float(data["revenue"] or 0),
                "sales": int(data["total_units"] or 0),
                "customers": int(data["customers"] or 0)
            })  

    except Exception as e:
        return jsonify({"error": str(e)}), 500
