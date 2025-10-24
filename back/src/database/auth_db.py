from ..index import db, bcrypt
from ..models.models import User

def create_new_user(username, password):
    """
    Create a new user in the database.
    """
    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return new_user