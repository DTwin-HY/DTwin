from os import getenv
from dotenv import load_dotenv
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
CORS(app, supports_credentials=True, origins=["http://localhost:5173"])

load_dotenv()

app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
app.config["SECRET_KEY"] = getenv("SECRET_KEY")

db = SQLAlchemy(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
bcrypt = Bcrypt(app)

#pylint: disable=wrong-import-position
#pylint: disable=unused-import
from . import routes


def start():
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=True)


if __name__ == "__main__":
    start()
