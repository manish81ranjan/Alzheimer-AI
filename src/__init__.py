# backend/src/middleware/rate_limit.py
"""
Simple in-memory rate limiter (development friendly).

NOTE:
- This resets on server restart
- For production, use Redis / API gateway rate limiting
"""

import time
from collections import defaultdict, deque
from functools import wraps
from flask import request, jsonify


# store timestamps for each key
_BUCKETS = defaultdict(lambda: deque(maxlen=200))


def rate_limit(max_requests: int = 60, per_seconds: int = 60, key_fn=None):
    """
    Decorator:
      @rate_limit(30, 60)  # 30 req/min

    key_fn: optional function returning a key string.
    Default key: IP + endpoint path
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            now = time.time()

            if key_fn:
                key = key_fn()
            else:
                ip = request.headers.get("X-Forwarded-For", request.remote_addr) or "unknown"
                path = request.path
                key = f"{ip}:{path}"

            q = _BUCKETS[key]

            # remove timestamps older than window
            while q and (now - q[0]) > per_seconds:
                q.popleft()

            if len(q) >= max_requests:
                return (
                    jsonify(
                        {
                            "success": False,
                            "message": "Too many requests. Try again later.",
                            "status": 429,
                        }
                    ),
                    429,
                )

            q.append(now)
            return fn(*args, **kwargs)

        return wrapper

    return decorator
