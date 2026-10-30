from __future__ import annotations

import os
from pathlib import Path
from typing import NamedTuple

ROOT = Path(__file__).resolve().parent.parent


def _load_dotenv() -> None:
    env_file = ROOT / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        text = line.strip()
        if not text or text.startswith("#") or "=" not in text:
            continue
        key, _, value = text.partition("=")
        os.environ.setdefault(key.strip(), value.strip())


_load_dotenv()


def database_path() -> Path:
    raw = os.environ.get("DATABASE_PATH", "data/reader.db")
    path = Path(raw)
    if not path.is_absolute():
        path = ROOT / path
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def git_sha() -> str:
    return os.environ.get("GIT_SHA", "dev")


def mail_imap_config() -> tuple[str, str, str] | None:
    host = os.environ.get("MAIL_IMAP_HOST")
    user = os.environ.get("MAIL_IMAP_USER")
    password = os.environ.get("MAIL_IMAP_PASSWORD")
    if not host or not user or not password:
        return None
    return host, user, password


def obsidian_github_token() -> str | None:
    return os.environ.get("OBSIDIAN_GITHUB_TOKEN")


def app_password() -> str | None:
    """The one password that opens the app. Without it nobody gets in."""
    return os.environ.get("READER_PASSWORD") or None


class AlertConfig(NamedTuple):
    host: str
    port: int
    user: str
    password: str
    to: str


def alert_config() -> AlertConfig | None:
    """Where sign-in alerts are sent from and to: out through the same Gmail
    account the app already reads newsletters from, to ALERT_EMAIL. Without
    both, no alert is sent."""
    mailbox = mail_imap_config()
    to = os.environ.get("ALERT_EMAIL")
    if mailbox is None or not to:
        return None
    imap_host, user, password = mailbox
    host = os.environ.get("MAIL_SMTP_HOST") or imap_host.replace("imap.", "smtp.", 1)
    return AlertConfig(host, 587, user, password, to)
