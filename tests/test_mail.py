from __future__ import annotations

from email.message import EmailMessage

import app.mail as mail
from app.db import (
    all_sources,
    connect,
    has_pending_source_notice,
    init_db,
    items_for_source,
    mark_sources_seen,
)
from app.mail import ingest_mail


def _raw(
    from_addr: str,
    subject: str,
    *,
    message_id: str = "<abc@example.test>",
    html_body: str | None = None,
    text_body: str | None = None,
) -> bytes:
    msg = EmailMessage()
    msg["From"] = from_addr
    msg["Subject"] = subject
    msg["Message-ID"] = message_id
    msg["Date"] = "Mon, 24 Aug 2026 08:00:00 +0000"
    if html_body is not None:
        msg.set_content(text_body or "plain fallback")
        msg.add_alternative(html_body, subtype="html")
    else:
        msg.set_content(text_body or "")
    return msg.as_bytes()


class FakeImapClient:
    def __init__(self, messages: dict[bytes, bytes]):
        self._messages = messages
        self.seen_uids: list[bytes] = []
        self.logged_out = False

    def select(self, mailbox):
        return ("OK", [b"1"])

    def uid(self, command, *args):
        if command == "search":
            return ("OK", [b" ".join(self._messages.keys())])
        if command == "fetch":
            uid = args[0]
            raw = self._messages.get(uid)
            if raw is None:
                return ("NO", [None])
            return ("OK", [(uid + b" (RFC822 {123}", raw)])
        if command == "store":
            self.seen_uids.append(args[0])
            return ("OK", [b"OK"])
        raise AssertionError(f"unexpected uid command: {command}")

    def logout(self):
        self.logged_out = True


def _configure_env(monkeypatch):
    monkeypatch.setenv("MAIL_IMAP_HOST", "imap.test")
    monkeypatch.setenv("MAIL_IMAP_USER", "reader@test")
    monkeypatch.setenv("MAIL_IMAP_PASSWORD", "app-password")


def test_ingest_mail_not_configured_returns_early(monkeypatch, tmp_path):
    conn = connect(tmp_path / "reader.db")
    init_db(conn)
    result = ingest_mail(conn)
    assert result == {"configured": False, "created": 0, "sources": 0}


def test_ingest_mail_connect_failure_does_not_raise(monkeypatch, tmp_path):
    _configure_env(monkeypatch)
    monkeypatch.setattr(mail, "_connect", lambda host, user, password: (_ for _ in ()).throw(OSError()))
    conn = connect(tmp_path / "reader.db")
    init_db(conn)
    result = ingest_mail(conn)
    assert result == {"configured": True, "connected": False, "created": 0, "sources": 0}


def test_ingest_mail_creates_source_and_marks_seen(monkeypatch, tmp_path):
    _configure_env(monkeypatch)
    raw = _raw(
        "Ann Author <ann@newsletter.test>",
        "First issue",
        html_body="<p>Hello <strong>reader</strong></p>",
    )
    client = FakeImapClient({b"1": raw})
    monkeypatch.setattr(mail, "_connect", lambda host, user, password: client)

    conn = connect(tmp_path / "reader.db")
    init_db(conn)
    result = ingest_mail(conn)
    conn.commit()

    assert result == {"configured": True, "connected": True, "created": 1, "sources": 1}
    assert client.seen_uids == [b"1"]
    assert client.logged_out

    sources = all_sources(conn)
    assert len(sources) == 1
    source = sources[0]
    assert source["kind"] == "mail"
    assert source["title"] == "Ann Author"
    assert source["mail_address"] == "ann@newsletter.test"
    assert source["pending_notice"] == 1

    items = items_for_source(conn, source["id"])
    assert len(items) == 1
    assert items[0]["title"] == "First issue"
    assert "Hello" in items[0]["body_html"]
    assert "<strong>reader</strong>" in items[0]["body_html"]

    assert has_pending_source_notice(conn) is True
    mark_sources_seen(conn)
    conn.commit()
    assert has_pending_source_notice(conn) is False


def test_ingest_mail_second_message_same_sender_reuses_source(monkeypatch, tmp_path):
    _configure_env(monkeypatch)
    first = _raw("ann@newsletter.test", "Issue 1", message_id="<one@test>", text_body="one")
    client = FakeImapClient({b"1": first})
    monkeypatch.setattr(mail, "_connect", lambda host, user, password: client)

    conn = connect(tmp_path / "reader.db")
    init_db(conn)
    ingest_mail(conn)
    conn.commit()
    mark_sources_seen(conn)
    conn.commit()

    second = _raw("ann@newsletter.test", "Issue 2", message_id="<two@test>", text_body="two")
    client2 = FakeImapClient({b"2": second})
    monkeypatch.setattr(mail, "_connect", lambda host, user, password: client2)
    result = ingest_mail(conn)
    conn.commit()

    assert result["sources"] == 1
    sources = all_sources(conn)
    assert len(sources) == 1
    assert sources[0]["pending_notice"] == 0
    items = items_for_source(conn, sources[0]["id"])
    assert len(items) == 2


def test_ingest_mail_no_address_skips_and_marks_seen(monkeypatch, tmp_path):
    _configure_env(monkeypatch)
    raw = _raw("", "No sender", text_body="body")
    client = FakeImapClient({b"1": raw})
    monkeypatch.setattr(mail, "_connect", lambda host, user, password: client)

    conn = connect(tmp_path / "reader.db")
    init_db(conn)
    result = ingest_mail(conn)
    conn.commit()

    assert result["created"] == 0
    assert result["sources"] == 0
    assert client.seen_uids == [b"1"]
    assert all_sources(conn) == []
