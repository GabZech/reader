from __future__ import annotations

import email
import imaplib
import sqlite3
from email.message import EmailMessage
from email.policy import default as email_policy
from email.utils import parseaddr, parsedate_to_datetime
from html import escape

from app.config import mail_imap_config
from app.db import (
    find_source_by_mail_address,
    insert_source,
    source_id_for_mail,
    upsert_item,
)
from app.ingest import sanitize_html, word_count


def _connect(host: str, user: str, password: str) -> imaplib.IMAP4_SSL:
    client = imaplib.IMAP4_SSL(host)
    client.login(user, password)
    return client


def _fetch_unseen(client: imaplib.IMAP4_SSL) -> list[tuple[bytes, EmailMessage]]:
    client.select("INBOX")
    status, data = client.uid("search", None, "UNSEEN")
    if status != "OK" or not data or not data[0]:
        return []
    messages = []
    for uid in data[0].split():
        status, msg_data = client.uid("fetch", uid, "(RFC822)")
        if status != "OK" or not msg_data or msg_data[0] is None:
            continue
        raw = msg_data[0][1]
        msg = email.message_from_bytes(raw, policy=email_policy)
        messages.append((uid, msg))
    return messages


def _mark_seen(client: imaplib.IMAP4_SSL, uid: bytes) -> None:
    client.uid("store", uid, "+FLAGS", "(\\Seen)")


def _extract_body_html(msg: EmailMessage) -> str:
    html_part = None
    text_part = None
    parts = msg.walk() if msg.is_multipart() else [msg]
    for part in parts:
        if part.get_content_disposition() == "attachment":
            continue
        ctype = part.get_content_type()
        if ctype == "text/html" and html_part is None:
            html_part = part
        elif ctype == "text/plain" and text_part is None:
            text_part = part
    if html_part is not None:
        return sanitize_html(html_part.get_content())
    if text_part is not None:
        paragraphs = [p.strip() for p in text_part.get_content().split("\n\n") if p.strip()]
        return "".join(f"<p>{escape(p)}</p>" for p in paragraphs)
    return ""


def _parse_date(raw: str | None) -> str | None:
    if not raw:
        return None
    try:
        return parsedate_to_datetime(raw).isoformat()
    except (TypeError, ValueError):
        return None


def ingest_mail(conn: sqlite3.Connection) -> dict:
    config = mail_imap_config()
    if config is None:
        return {"configured": False, "created": 0, "sources": 0}
    host, user, password = config
    try:
        client = _connect(host, user, password)
    except (OSError, imaplib.IMAP4.error):
        return {"configured": True, "connected": False, "created": 0, "sources": 0}

    created = 0
    touched: set[str] = set()
    try:
        messages = _fetch_unseen(client)
        for uid, msg in messages:
            try:
                name, address = parseaddr(msg.get("From", ""))
                if not address:
                    _mark_seen(client, uid)
                    continue
                source = find_source_by_mail_address(conn, address)
                if source is None:
                    title = name or address
                    source_id = source_id_for_mail(address)
                    insert_source(
                        conn,
                        source_id=source_id,
                        kind="mail",
                        title=title,
                        feed_url=None,
                        backfill=None,
                        auto_title=title,
                        mail_address=address,
                        pending_notice=True,
                    )
                else:
                    source_id = source["id"]
                touched.add(source_id)
                body_html = _extract_body_html(msg)
                guid = msg.get("Message-ID") or (
                    f"{address}:{msg.get('Date', '')}:{msg.get('Subject', '')}"
                )
                is_new = upsert_item(
                    conn,
                    source_id=source_id,
                    guid=str(guid),
                    title=msg.get("Subject") or "(no subject)",
                    author=name or address,
                    url=None,
                    published_at=_parse_date(msg.get("Date")),
                    body_html=body_html,
                    image_url=None,
                    word_count=word_count(body_html),
                )
                if is_new:
                    created += 1
                _mark_seen(client, uid)
            except Exception:
                continue
    finally:
        try:
            client.logout()
        except Exception:
            pass
    return {"configured": True, "connected": True, "created": created, "sources": len(touched)}
