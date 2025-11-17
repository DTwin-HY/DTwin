from uuid import uuid4

from ..database.supervisor_db import check_thread_id_exists


def generate_unique_thread_id(max_tries: int = 5) -> str:
    """Generate a thread_id that doesn't yet exist in the Chat table."""

    for _ in range(max_tries):
        candidate = uuid4().hex
        if not check_thread_id_exists(candidate):
            return candidate
    raise RuntimeError("Could not generate unique thread_id after several attempts")
