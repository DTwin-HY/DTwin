from flask_login import UserMixin
<<<<<<< HEAD:back/main/models.py

from main.index import db
=======
from back.index import db
>>>>>>> f31294b (Refactor the backend and removed useless imports):back/main/models/models.py


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
