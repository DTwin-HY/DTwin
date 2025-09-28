from back.index import app, db, bcrypt, login_manager
from flask import jsonify, request
from flask_login import login_user, logout_user, login_required, current_user
from main.models.models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.post("/api/signup")
def signup():
    """
    create a new user and log them in
    """
    data = request.json
    username = data["username"]
    password = data["password"]

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already taken"}), 409

    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    login_user(new_user)
    return jsonify({"message": "User created", "user": {"username": new_user.username}})

@app.post("/api/signin")
def signin():
    """
    log in an existing user
    """
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password required"})

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"error": "Invalid username or password"}), 401
    if not bcrypt.check_password_hash(user.password, password):
        return jsonify({"error": "Invalid username or password"}), 401

    login_user(user, remember=True)
    return jsonify({"message": "Login successful! Welcome", "user": {"username": user.username}})

@app.post("/api/logout")
@login_required
def logout():
    """
    log out the current user
    """
    logout_user()
    return jsonify({"message": "Logged out successfully"})

@app.get("/api/check_auth")
def check_auth():
    """
    check if the user is logged in
    """
    if current_user.is_authenticated:
        return jsonify({"authenticated": True, "user": {"username": current_user.username}})
    else:
        return jsonify({"authenticated": False, "user": None})
