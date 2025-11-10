import os
from datetime import datetime, timedelta

from flask import Flask, jsonify, request

from ..database.sales import fetch_sales_data
from ..extensions import db
from ..index import app


@app.get("/api/sales-data")
def get_sales_data():
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")

    if not start_date or not end_date:
        return jsonify({"error": "start_date and end_date are required"}), 400

    try:
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")

        # Set end time to 23:59:59 to include the entire end day
        end = end.replace(hour=23, minute=59, second=59)

        summary = fetch_sales_data(start, end)
        return jsonify(summary)

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e), "revenue": 0, "sales": 0, "transactions": 0}), 500
