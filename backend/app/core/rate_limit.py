import time
from collections import defaultdict
from typing import Dict, List
from fastapi import Request

from app.core.exceptions import RateLimitError


class InMemoryRateLimiter:
    """
    Sliding window in-memory rate limiter keyed by client identifier.
    Thread-safe within Python's async event loop.
    """

    def __init__(self, requests_limit: int = 10, window_seconds: int = 60) -> None:
        self.requests_limit = requests_limit
        self.window_seconds = window_seconds
        self.hits: Dict[str, List[float]] = defaultdict(list)

    def check(self, key: str) -> None:
        now = time.time()
        window_start = now - self.window_seconds
        timestamps = self.hits[key]
        # Keep only timestamps within sliding window
        valid_timestamps = [t for t in timestamps if t > window_start]
        if len(valid_timestamps) >= self.requests_limit:
            self.hits[key] = valid_timestamps
            raise RateLimitError(
                f"Rate limit exceeded. Maximum {self.requests_limit} requests per {self.window_seconds} seconds."
            )
        valid_timestamps.append(now)
        self.hits[key] = valid_timestamps

    def reset(self) -> None:
        """Reset all rate limiter tracking (used in tests)."""
        self.hits.clear()


auth_rate_limiter = InMemoryRateLimiter(requests_limit=10, window_seconds=60)


async def rate_limit_auth(request: Request) -> None:
    """Dependency guard to throttle authentication attempts by client IP."""
    client_ip = request.client.host if request.client else "unknown"
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        client_ip = forwarded.split(",")[0].strip()
    auth_rate_limiter.check(client_ip)
