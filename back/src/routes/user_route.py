from flask_login import current_user, login_required

from ..index import app


@app.get("/api/me")
@login_required
def me():
    """Return information about the current logged-in user."""
    return {"user_id": current_user.id} #pragma: no cover
