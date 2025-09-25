from back.index import db

class History(db.Model):
    __tablename__ = "history"
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    event_type = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Integer, nullable=False)

    product = db.relationship("Product", backref="history_events")