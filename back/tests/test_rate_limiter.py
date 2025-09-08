import pytest
from main.utils.rate_limiter import RateLimiter


def test_under_limit(monkeypatch):
    '''
    check if calls under limit are allowed
    '''
    limiter = RateLimiter(max_calls=3, interval=10)

    fake_time = [1]

    def fake_time_fn():
        return fake_time[0]

    monkeypatch.setattr("time.time", fake_time_fn)

    for _ in range(3):
        limiter.check()

    fake_time[0] = 3
    assert len(limiter.call_times) == 3


def test_exceed_limit(monkeypatch):
    '''
    check if exceeding the limit raises an error
    '''
    limiter = RateLimiter(max_calls=2, interval=10)

    fake_time = [1]

    def fake_time_fn():
        return fake_time[0]

    monkeypatch.setattr("time.time", fake_time_fn)

    limiter.check()
    limiter.check()

    with pytest.raises(RuntimeError):
        limiter.check()


def test_limit_resets_after_interval(monkeypatch):
    '''
    check if limit resets after the interval
    '''
    limiter = RateLimiter(max_calls=2, interval=5)

    fake_time = [1]

    def fake_time_fn():
        return fake_time[0]

    monkeypatch.setattr("time.time", fake_time_fn)

    limiter.check()

    fake_time[0] = 3
    limiter.check()

    fake_time[0] = 7
    limiter.check()
    assert len(limiter.call_times) == 2
