from flask import Flask, jsonify, request, abort
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from main.chatgpt.chat import answer
from main.chatgpt.main import run_multiple_conversations
from os import getenv
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app, supports_credentials=True, origins=["http://localhost:5173"])

app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
app.config["SECRET_KEY"] = getenv("SECRET_KEY")
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
bcrypt = Bcrypt(app)

@app.get("/api/ping")
def ping():
    return jsonify({"ok": True, "message": "pong"})

@app.get("/")
def home():
    return (jsonify({"ok": True, "message": "welcome to dtwin!"}))

@app.post("/api/echo")
@login_required
def echo():
    if not request.is_json:
        abort(400, description="Body must be JSON")
    data = request.get_json()
    print(data)
    output = answer(data["message"])

    sql = text("INSERT INTO logs (prompt, reply) VALUES (:prompt, :reply);")
    db.session.execute(sql, {"prompt":data["message"], "reply": output["message"]})
    db.session.commit()

    return jsonify(output)

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.post("/api/signup")
def signup():
    data = request.json
    username = data["username"]
    password = data["password"]

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already taken"})

    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    login_user(new_user)
    return jsonify({"message": "User created", "user": {"username": new_user.username}})

@app.post("/api/signin")
def signin():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password required"})

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "Invalid username or password"})
    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({"error": "Invalid username or password"})

    login_user(user, remember=True)
    return jsonify({"message": "Login successful! Welcome", "user": {"username": user.username}})

@app.post("/api/logout")
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out successfully"})

@app.get("/api/check_auth")
def check_auth():
    if current_user.is_authenticated:
        return jsonify({"authenticated": True, "user": {"username": current_user.username}})
    else:
        return jsonify({"authenticated": False, "user": None})

'''
return a user-friendly name for an item_id
'''
def item_name(item_id):
    names = {
        "strawberries_small": "Small box of strawberries",
        "strawberries_medium": "Medium box of strawberries"
    }
    return names.get(item_id, item_id)

@app.get("/api/sales")
@login_required
def get_sales():
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

    sales = [
        {
            "transaction_id": row["transaction_id"],
            "item_id": row["item_id"],
            "item_name": item_name(row["item_id"]),
            "quantity": row["quantity"],
            "amount": float(row["amount"]),
            "timestamp": row["timestamp"].isoformat()
        }
        for row in result.mappings()
    ]
    return jsonify({"sales": sales})

@app.post("/api/simulate-sales")
@login_required
def simulate_sales():
    if not request.is_json:
        abort(400, description="Body must be JSON")
    
    data = request.get_json()
    date_str = data.get("date")
    
    if not date_str:
        return jsonify({"error": "Date is required"}), 400

    try:       
        print(f"Starting full day sales simulation for {date_str}...")

        result = run_multiple_conversations(2)
        for i in result["sales"]:
            i["item_name"] = item_name(i.get("item_id"))
        return jsonify(result)
        
    except ValueError as e:
        return jsonify({"error": f"Invalid date format: {str(e)}"}), 400
    except Exception as e:
        print(f"Error during simulation: {str(e)}")
        return jsonify({"error": f"Simulation failed: {str(e)}"}), 500

def start():
    app.run(host="0.0.0.0", port=5000, debug=True)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    start()