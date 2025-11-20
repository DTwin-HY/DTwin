from sqlalchemy import text

from ..extensions import db
from ..index import app


def fetch_product_data():
    """
    Execute the sales summary query between start and end datetimes.
    """
    sql_query = text("""SELECT id, price FROM products;""")

    # Tarvitaan app-konteksti, jotta db.session toimii
    with app.app_context():
        try:
            rows = db.session.execute(sql_query).mappings().all()

            product_price_map = {
                str(row["id"]): float(row["price"])
                for row in rows
            }

            return product_price_map

        except Exception:
            db.session.rollback()
            raise
