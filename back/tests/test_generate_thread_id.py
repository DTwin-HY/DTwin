import pytest

from src.utils import generate_thread_id as gt


def test_generate_unique_thread_id_returns_hex_and_calls_check(monkeypatch):
    """
    First case: generate_unique_thread_id returns a hex string of length 32,
    and calls the check function at least once.
    """

    calls = {"count": 0}

    def fake_check(candidate: str) -> bool:
        calls["count"] += 1
        # Not found in DB → ok to use this
        return False

    # Monkeypatch the generate_thread_id module's own check function
    monkeypatch.setattr(gt, "check_thread_id_exists", fake_check)

    thread_id = gt.generate_unique_thread_id()

    assert isinstance(thread_id, str)
    # uuid4().hex is 32 characters long
    assert len(thread_id) == 32
    # Ensure the check was called at least once
    assert calls["count"] == 1


def test_generate_unique_thread_id_retries_until_free(monkeypatch):
    """
    Case: first two generated candidates 'collide', third is free.
    """

    # Generate deterministic candidate IDs
    candidates = ["a" * 32, "b" * 32, "c" * 32]

    class FakeUUID:
        def __init__(self, value: str):
            self._value = value

        @property
        def hex(self) -> str:
            return self._value

    def fake_uuid4():
        return FakeUUID(candidates.pop(0))

    def fake_check(candidate: str) -> bool:
        # First two exist, third does not
        return candidate in {"a" * 32, "b" * 32}

    monkeypatch.setattr(gt, "uuid4", fake_uuid4)
    monkeypatch.setattr(gt, "check_thread_id_exists", fake_check)

    thread_id = gt.generate_unique_thread_id(max_tries=5)

    assert thread_id == "c" * 32  # third candidate was the first free one


def test_generate_unique_thread_id_raises_after_max_tries(monkeypatch):
    """
    Case: all attempts 'collide' → RuntimeError after max_tries.
    """

    def always_exists(candidate: str) -> bool:
        return True  # every candidate 'exists'

    monkeypatch.setattr(gt, "check_thread_id_exists", always_exists)

    with pytest.raises(RuntimeError):
        gt.generate_unique_thread_id(max_tries=3)
