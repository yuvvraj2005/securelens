"""
Two lightweight FastAPI dependencies:

  - require_api_key: validates the X-API-Key header against the configured
    API_KEYS set. If AUTH_ENABLED is False (no keys configured), it's a
    no-op — this is meant for local dev only, see .env.example.

  - enforce_rate_limit: a simple in-memory sliding-window limiter keyed by
    API key (or client IP if auth is disabled). Good enough for a single
    backend process; if you scale to multiple instances, swap this for a
    Redis-backed limiter (e.g. via `slowapi` + Redis storage) so the count
    is shared across processes instead of per-instance.
"""

import time
import threading
from collections import defaultdict, deque

from fastapi import Header, HTTPException, Request

from backend.app.core.config import (
    API_KEYS,
    AUTH_ENABLED,
    RATE_LIMIT_ENABLED,
    RATE_LIMIT_SCANS_PER_HOUR,
)

_WINDOW_SECONDS = 3600
_hits: dict[str, deque] = defaultdict(deque)
_lock = threading.Lock()


def require_api_key(x_api_key: str | None = Header(default=None)) -> str:
    """Returns an identifier for the caller (the API key, or 'anonymous'
    when auth is disabled) so downstream code can use it for rate
    limiting / audit logging."""
    if not AUTH_ENABLED:
        return "anonymous"

    if not x_api_key or x_api_key not in API_KEYS:
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid X-API-Key header.",
        )

    return x_api_key


def enforce_rate_limit(request: Request, api_key: str = None) -> None:
    """Call after require_api_key. Keyed by api_key when auth is on,
    otherwise falls back to the client's IP address."""
    if not RATE_LIMIT_ENABLED:
        return

    identity = api_key if (api_key and api_key != "anonymous") else (
        request.client.host if request.client else "unknown"
    )

    now = time.time()

    with _lock:
        window = _hits[identity]

        while window and window[0] < now - _WINDOW_SECONDS:
            window.popleft()

        if len(window) >= RATE_LIMIT_SCANS_PER_HOUR:
            retry_after = int(_WINDOW_SECONDS - (now - window[0]))
            raise HTTPException(
                status_code=429,
                detail=(
                    f"Rate limit exceeded: {RATE_LIMIT_SCANS_PER_HOUR} scans/hour. "
                    f"Try again in ~{retry_after}s."
                ),
            )

        window.append(now)
