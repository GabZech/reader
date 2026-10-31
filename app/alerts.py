"""Email alerts about who is signing in: a new sign-in, or a network locked out.

Sent through the mailbox the app already holds, in the background, and never
allowed to get in the way of signing in: a failure is noted in Diagnostics.
"""

from __future__ import annotations

import smtplib
from datetime import timedelta, timezone
from email.message import EmailMessage

from app import auth, diag
from app.config import alert_config

# Brasilia has no daylight saving: a fixed offset is exact.
LOCAL_TIMEZONE = timezone(timedelta(hours=-3), "BRT")


def _send(subject: str, body: str) -> None:
    config = alert_config()
    if config is None:
        return
    message = EmailMessage()
    message["From"] = config.user
    message["To"] = config.to
    message["Subject"] = subject
    message.set_content(body)
    try:
        with smtplib.SMTP(config.host, config.port, timeout=15) as server:
            server.starttls()
            server.login(config.user, config.password)
            server.send_message(message)
    except OSError as error:  # includes every smtplib error, refusals and timeouts too
        diag.note("alert-failed", f"{type(error).__name__}: {error}")


def _when() -> str:
    return auth.now().astimezone(LOCAL_TIMEZONE).strftime("%d %b %Y, %H:%M (Brasilia)")


def new_sign_in(device_name: str, client: str) -> None:
    _send(
        f"Reader: new sign-in from {device_name}",
        f"A browser just signed in to Reader.\n\n"
        f"Device: {device_name}\n"
        f"Network: {client}\n"
        f"When: {_when()}\n\n"
        "If this was you, nothing to do. If not, open Settings, Devices and revoke it, "
        "then change the password on Fly.",
    )


def locked_out(client: str) -> None:
    _send(
        "Reader: sign-in locked after wrong passwords",
        f"Several wrong passwords were tried on Reader's login page.\n\n"
        f"Network: {client}\n"
        f"When: {_when()}\n\n"
        f"That network is locked out for {auth.minutes_left(auth.LOCK_FOR)}. "
        "Nothing was let in. If you did not try this, consider changing the password on Fly.",
    )
