"""A short in-memory trace of what the phone and the server did.

It exists to track down a white screen that only shows on an iPhone. Nothing
is stored on disk: a restart or deploy clears it, and `started_at` says when
that last happened, which is itself a clue.
"""

from __future__ import annotations

import time
from collections import deque
from datetime import UTC, datetime

MAX_EVENTS = 1500
MAX_REQUESTS = 400
MAX_BODY_BYTES = 64_000
MAX_BATCH = 100

# Paths that would only add noise to the request trace.
QUIET_PATHS = {"/health", "/diag", "/diagnostics", "/sw.js", "/manifest.webmanifest", "/favicon.ico"}

_started = datetime.now(UTC)
_events: deque[dict] = deque()
_seen: set[tuple[str, int]] = set()
_requests: deque[dict] = deque(maxlen=MAX_REQUESTS)
_in_flight = 0


def reset() -> None:
    global _in_flight
    _events.clear()
    _seen.clear()
    _requests.clear()
    _in_flight = 0


def _text(value: object, limit: int) -> str:
    return value[:limit] if isinstance(value, str) else ""


def _number(value: object) -> int:
    return value if isinstance(value, int) and not isinstance(value, bool) else 0


def _clean(raw: object) -> dict | None:
    if not isinstance(raw, dict):
        return None
    return {
        "s": _number(raw.get("s")),
        "t": _number(raw.get("t")),
        "e": _text(raw.get("e"), 40),
        "p": _text(raw.get("p"), 80),
        "d": _text(raw.get("d"), 200),
        "n": _text(raw.get("n"), 12),
        "l": _text(raw.get("l"), 12),
    }


def record_events(batch: list) -> None:
    """Keep what the phone reports, skipping junk and anything already seen."""
    for raw in batch[:MAX_BATCH]:
        event = _clean(raw)
        if event is None:
            continue
        key = (event["l"], event["s"])
        if key in _seen:
            continue
        _seen.add(key)
        _events.append(event)
        while len(_events) > MAX_EVENTS:
            old = _events.popleft()
            _seen.discard((old["l"], old["s"]))


def request_started() -> tuple[float, int]:
    """Note a request arriving; returns what `request_finished` needs."""
    global _in_flight
    busy = _in_flight
    _in_flight += 1
    return time.monotonic(), busy


def request_finished(method: str, path: str, status: int, started: tuple[float, int]) -> None:
    global _in_flight
    _in_flight = max(0, _in_flight - 1)
    began, busy = started
    _requests.append(
        {
            "at": datetime.now(UTC).strftime("%H:%M:%S"),
            "method": method,
            "path": path[:80],
            "status": status,
            "ms": int((time.monotonic() - began) * 1000),
            "busy": busy,
        }
    )


def snapshot() -> dict:
    now = datetime.now(UTC)
    return {
        "started_at": _started.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "uptime_s": int((now - _started).total_seconds()),
        "events": list(_events),
        "requests": list(_requests),
    }
