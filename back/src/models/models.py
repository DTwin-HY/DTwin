from flask_login import UserMixin
from ..index import db

from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)


class Log(db.Model):
    __tablename__ = "logs"
    id = db.Column(db.Integer, primary_key=True)
    prompt = db.Column(db.Text, nullable=False)
    reply = db.Column(db.Text, nullable=False)


class Sale(db.Model):
    __tablename__ = "sales"
    id = db.Column(db.Integer, primary_key=True)
    transaction_id = db.Column(db.String(36), nullable=False)
    item_id = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=True)


class Product(db.Model):
    __tablename__ = "products"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)


class Inventory(db.Model):
    __tablename__ = "inventory"
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer, nullable=False, default=0)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)

    product = db.relationship("Product", backref="inventory_items")


class Counter(db.Model):
    __tablename__ = "counter"
    id = db.Column(db.Integer, primary_key=True)
    balance = db.Column(db.Numeric(10, 2), nullable=False, default=0)


class History(db.Model):
    __tablename__ = "history"
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime, nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    event_type = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Integer, nullable=False)

    product = db.relationship("Product", backref="history_events")
