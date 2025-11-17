from flask_login import login_required, current_user
from ..index import app

@app.get("/api/me")
@login_required
def me():
    """Return information about the current logged-in user."""
    return {"user_id": current_user.id}
