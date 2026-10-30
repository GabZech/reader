"""The password gate: who gets in, how a device stays in, who is locked out.

One password, set as the LOGIN_PASSWORD secret. A correct password gives
that browser a cookie; the server keeps only a hash of it, in the `devices`
table. A browser stays in until it goes unused for IDLE_LIMIT, is revoked, or
the password changes (each sign-in is tied to the password it was made with).
"""

from __future__ import annotations

import hashlib
import hmac
import math
import secrets
import sqlite3
from datetime import UTC, datetime, timedelta, tzinfo
from functools import lru_cache
from urllib.parse import urlencode

from fastapi import Request
from fastapi.responses import RedirectResponse, Response

from app.config import app_password
from app.db import delete_device, find_device, touch_device

SESSION_COOKIE = "reader_session"
# Browsers cap a cookie's life at about this; the server's own idle limit
# is what actually ends a sign-in.
COOKIE_MAX_AGE = 400 * 24 * 3600
IDLE_LIMIT = timedelta(days=30)
# "Last used" is written at most this often, not on every tap.
TOUCH_EVERY = timedelta(minutes=5)
LOCK_AFTER = 5
LOCK_FOR = timedelta(minutes=15)

# Open to anyone: the health check, the login page, and what every page
# needs to draw itself.
OPEN_PATHS = {"/health", "/login", "/sw.js", "/manifest.webmanifest", "/favicon.ico"}


def now() -> datetime:
    return datetime.now(UTC)


def is_open(path: str) -> bool:
    return path in OPEN_PATHS or path.startswith("/static/")


def token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def new_token() -> str:
    return secrets.token_urlsafe(32)


# ---------- the password ----------


def password_matches(candidate: str) -> bool:
    expected = app_password()
    if not expected:
        return False
    # Hashed first so the comparison takes the same time whatever the length.
    return hmac.compare_digest(
        hashlib.sha256(candidate.encode()).digest(), hashlib.sha256(expected.encode()).digest()
    )


@lru_cache(maxsize=4)
def _epoch_of(password: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode(), b"reader-sign-in", 100_000).hex()[:32]


def epoch() -> str | None:
    """Stands for the current password: a browser signed in under another one
    is signed out. Not the password itself, and slow to guess from."""
    password = app_password()
    return _epoch_of(password) if password else None


# ---------- who is signed in ----------


def signed_in_device(conn: sqlite3.Connection, token: str | None) -> sqlite3.Row | None:
    if not token or epoch() is None:
        return None
    device = find_device(conn, token_hash(token))
    # A save key is not a sign-in, whatever it is presented as.
    if device is None or device["kind"] != "browser":
        return None
    moment = now()
    if device["epoch"] != epoch():
        delete_device(conn, device["id"])
        conn.commit()
        return None
    idle = moment - datetime.fromisoformat(device["last_used_at"])
    if idle > IDLE_LIMIT:
        delete_device(conn, device["id"])
        conn.commit()
        return None
    _note_used(conn, device, idle, moment)
    return device


def _note_used(conn: sqlite3.Connection, device: sqlite3.Row, idle: timedelta, moment: datetime):
    # Not on every tap, but a key's first use always: "not used yet" must go away.
    first_use = device["kind"] == "key" and device["created_at"] == device["last_used_at"]
    if idle >= TOUCH_EVERY or first_use:
        touch_device(conn, device["id"], moment)
        conn.commit()


def new_key() -> str:
    return "rk_" + secrets.token_urlsafe(24)


def valid_save_key(conn: sqlite3.Connection, key: str | None) -> sqlite3.Row | None:
    """A save key can send a page to Read later and nothing else. It does not
    expire and does not depend on the password, but with no password set the
    app is closed to everyone."""
    if not key or not app_password():
        return None
    device = find_device(conn, token_hash(key))
    if device is None or device["kind"] != "key":
        return None
    moment = now()
    _note_used(conn, device, moment - datetime.fromisoformat(device["last_used_at"]), moment)
    return device


def wants_page(request: Request) -> bool:
    """Whether a person is opening a page, rather than the app fetching data.
    The phone's own background fetches must never be sent to the login page:
    followed, it would be stored as the page they asked for."""
    mode = request.headers.get("sec-fetch-mode")
    if mode:
        return mode == "navigate"
    return "text/html" in request.headers.get("accept", "")


def turn_away(request: Request) -> Response:
    if not wants_page(request):
        return Response("Sign in required", status_code=401, headers={"Cache-Control": "no-store"})
    target = "/login"
    if request.method == "GET":
        where = request.url.path + (f"?{request.url.query}" if request.url.query else "")
        target = "/login?" + urlencode({"next": where})
    return RedirectResponse(target, status_code=303)


def safe_next(target: str | None) -> str:
    """Where to go after signing in: a path on this app, nothing else."""
    if not target or not target.startswith("/") or target.startswith(("//", "/\\")):
        return "/"
    return target


# ---------- guessing ----------

_failures: dict[str, list[datetime]] = {}
_locked_until: dict[str, datetime] = {}


def client_id(request: Request) -> str:
    # The host's own header: X-Forwarded-For can be written by anyone.
    return request.headers.get("fly-client-ip") or (
        request.client.host if request.client else "unknown"
    )


def forget_failed_logins() -> None:
    _failures.clear()
    _locked_until.clear()


def locked_for(client: str) -> timedelta | None:
    until = _locked_until.get(client)
    if until is None:
        return None
    left = until - now()
    if left <= timedelta(0):
        del _locked_until[client]
        return None
    return left


def note_failed_login(client: str) -> bool:
    """Count a wrong password. True when this one started a lockout."""
    moment = now()
    for other in [c for c, until in _locked_until.items() if until <= moment]:
        del _locked_until[other]
    # Networks whose wrong tries have all aged out are forgotten, so the
    # table cannot grow without end.
    for other in [c for c, tries in _failures.items() if moment - tries[-1] >= LOCK_FOR]:
        del _failures[other]
    recent = [t for t in _failures.get(client, []) if moment - t < LOCK_FOR]
    recent.append(moment)
    locked = len(recent) >= LOCK_AFTER
    if locked:
        _locked_until[client] = moment + LOCK_FOR
        recent = []
    if recent:
        _failures[client] = recent
    else:
        _failures.pop(client, None)
    return locked


def note_good_login(client: str) -> None:
    _failures.pop(client, None)


def minutes_left(left: timedelta) -> str:
    minutes = max(1, math.ceil(left.total_seconds() / 60))
    return f"{minutes} minute" if minutes == 1 else f"{minutes} minutes"


# ---------- naming a device ----------


def device_name(user_agent: str, installed: bool = False) -> str:
    agent = user_agent or ""
    system = next(
        (
            label
            for needle, label in (
                ("iPhone", "iPhone"),
                ("iPad", "iPad"),
                ("Android", "Android"),
                ("CrOS", "ChromeOS"),
                ("Windows", "Windows"),
                ("Macintosh", "Mac"),
                ("Linux", "Linux"),
                ("X11", "Linux"),
            )
            if needle in agent
        ),
        None,
    )
    browser = next(
        (
            label
            for needles, label in (
                (("Edg/", "EdgA/", "EdgiOS/"), "Edge"),
                (("OPR/", "Opera"), "Opera"),
                (("Firefox/", "FxiOS/"), "Firefox"),
                (("CriOS/", "Chrome/"), "Chrome"),
                (("Safari/", "Version/"), "Safari"),
            )
            if any(needle in agent for needle in needles)
        ),
        None,
    )
    name = " · ".join(part for part in (system, browser) if part) or "Unknown device"
    return f"{name} (installed app)" if installed else name


# ---------- saying it in words ----------


def signed_in_words(stamp: str, zone: tzinfo) -> str:
    when = datetime.fromisoformat(stamp).astimezone(zone)
    today = now().astimezone(zone)
    if when.date() == today.date():
        return f"today, {when:%H:%M}"
    day = f"{when.day} {when:%b}"
    return day if when.year == today.year else f"{day} {when.year}"


def last_used_words(stamp: str) -> str:
    seconds = (now() - datetime.fromisoformat(stamp)).total_seconds()
    if seconds < 120:
        return "just now"
    if seconds < 3600:
        return f"{int(seconds // 60)} minutes ago"
    if seconds < 86400:
        hours = int(seconds // 3600)
        return "1 hour ago" if hours == 1 else f"{hours} hours ago"
    days = int(seconds // 86400)
    return "yesterday" if days == 1 else f"{days} days ago"
