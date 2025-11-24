from flask import jsonify

from ..utils.dashboard import fetch_dashboard_data
from ..extensions import db
from ..index import app


@app.get("/api/dashboard-data")
def get_dashboard_data():

    try:
        data = fetch_dashboard_data()
        return jsonify(data)
    
    except Exception as e:

        return jsonify({"error": str(e)})