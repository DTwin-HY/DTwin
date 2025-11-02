# pylint: disable=too-few-public-methods
from flask_login import UserMixin
from sqlalchemy.dialects.postgresql import JSONB

from ..extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    # lazy="dynamic" -> palauttaa Query-olion (ei listaa)
    # cascade="all, delete-orphan" -> ketjuttaa operaatiot; poistaa orvot
    # passive_deletes=True -> anna DB:n ON DELETE CASCADE hoitaa poistot
    chats = db.relationship(
        "Chat", backref="user", lazy="dynamic", cascade="all, delete-orphan", passive_deletes=True
    )


class Chat(db.Model):
    __tablename__ = "chat"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    # JSONB = Postgresin natiivi JSON-tyyppi (haku/indeksointi mahdollista)
    # default=list = luo uuden tyhjän listan per rivi (ei jaettua []-objektia)
    messages = db.Column(JSONB, nullable=False, default=list)
    thread_id = db.Column(db.String(128), unique=True, index=True, nullable=False)
    # server_default=now() = DB täyttää arvon INSERTissä
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    # onupdate.db.func.=now() = päivittää updated_at-arvon UPDATE:ssa
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    raw_stream = db.Column(db.Text)


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
