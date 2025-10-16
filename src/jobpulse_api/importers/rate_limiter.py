"""Simple rate limiter using token bucket"""
import asyncio
import time
class RateLimiter:
    """Token bucket rate limiter"""
    def __init__(self, rate: float = 5.0, burst: int = 10):
        """
        Args:
            rate: requests per second
            burst: max requests in burst
        """
        self.rate = rate
        self.burst = burst
        self.tokens = burst
        self.last_update = time.time()
        self._lock = asyncio.Lock()
    async def acquire(self):
        """Wait until a token is available"""
        async with self._lock:
            now = time.time()
            elapsed = now - self.last_update
            self.tokens = min(self.burst, self.tokens + elapsed * self.rate)
            self.last_update = now
            if self.tokens < 1:
                wait_time = (1 - self.tokens) / self.rate
                await asyncio.sleep(wait_time)
                self.tokens = 0
            else:
                self.tokens -= 1
