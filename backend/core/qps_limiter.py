# backend/core/qps_limiter.py
import time
import threading

class TokenBucket:
    def __init__(self, rate: float, capacity: float=None):
        self.rate = rate
        self.capacity = capacity if capacity else rate
        self._tokens = self.capacity
        self._last = time.time()
        self._lock = threading.Lock()

    def consume(self, tokens: float=1.0) -> bool:
        with self._lock:
            now = time.time()
            elapsed = now - self._last
            self._tokens = min(self.capacity, self._tokens + elapsed * self.rate)
            self._last = now
            if self._tokens >= tokens:
                self._tokens -= tokens
                return True
            return False

# usage example: per-service limiters dict
_limiters = {}

def get_limiter(service: str, qps: float):
    if service not in _limiters:
        _limiters[service] = TokenBucket(rate=qps, capacity=max(1, qps))
    return _limiters[service]
