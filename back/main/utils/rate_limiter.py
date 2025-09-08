import time
from collections import deque

class RateLimiter:
    def __init__(self, max_calls: int, interval: int):
        """
        max_calls: maximum number of calls allowed within the interval
        interval: time window in seconds
        """
        self.max_calls = max_calls
        self.interval = interval
        self.call_times = deque()

    def check(self):
        """
        check if a new call can be made, raises RuntimeError if limit is exceeded
        """
        now = time.time()
        while self.call_times and now - self.call_times[0] > self.interval:
            self.call_times.popleft()

        if len(self.call_times) >= self.max_calls:
            raise RuntimeError("Too many API calls in a short period")

        self.call_times.append(now)
