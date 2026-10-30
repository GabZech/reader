"""Email alerts: a new sign-in, or a network locked out for guessing."""

from __future__ import annotations

from typing import ClassVar

import pytest
from conftest import TEST_PASSWORD
from fastapi.testclient import TestClient

from app import alerts, auth, diag
from app.config import alert_config
from app.main import app

IPHONE = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 "
    "(KHTML, like Gecko) Version/18.0 Mobile/15E148 Safari/604.1"
)


class FakeSMTP:
    sent: ClassVar[list] = []
    log: ClassVar[list] = []
    fail = False

    def __init__(self, host, port=0, timeout=None):
        FakeSMTP.log.append(("connect", host, port))

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def starttls(self, **kwargs):
        FakeSMTP.log.append(("starttls",))

    def login(self, user, password):
        FakeSMTP.log.append(("login", user, password))
        if FakeSMTP.fail:
            raise OSError("mail server down")

    def send_message(self, message):
        FakeSMTP.sent.append(message)


@pytest.fixture(autouse=True)
def _mail(anonymous, monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "reader.db"))
    monkeypatch.setenv("MAIL_IMAP_HOST", "imap.example.test")
    monkeypatch.setenv("MAIL_IMAP_USER", "reader-box@example.test")
    monkeypatch.setenv("MAIL_IMAP_PASSWORD", "app-password")
    monkeypatch.setenv("ALERT_EMAIL", "me@example.test")
    monkeypatch.delenv("MAIL_SMTP_HOST", raising=False)
    FakeSMTP.sent, FakeSMTP.log, FakeSMTP.fail = [], [], False
    monkeypatch.setattr(alerts.smtplib, "SMTP", FakeSMTP)
    diag.reset()


def _client():
    return TestClient(app, follow_redirects=False)


def _sign_in(client, password=TEST_PASSWORD, **headers):
    return client.post("/login", data={"password": password}, headers=headers)


def test_a_new_sign_in_is_emailed_with_what_the_owner_needs_to_judge_it():
    response = _sign_in(_client(), **{"User-Agent": IPHONE, "Fly-Client-IP": "203.0.113.9"})
    assert response.status_code == 303
    (message,) = FakeSMTP.sent
    assert message["To"] == "me@example.test"
    assert message["From"] == "reader-box@example.test"
    assert "new sign-in" in message["Subject"].lower()
    assert "iPhone · Safari" in message["Subject"]
    body = message.get_content()
    assert "iPhone · Safari" in body
    assert "203.0.113.9" in body
    assert "Devices" in body


def test_the_mail_goes_through_the_mailbox_the_app_already_has():
    _sign_in(_client())
    assert ("connect", "smtp.example.test", 587) in FakeSMTP.log
    assert ("starttls",) in FakeSMTP.log
    assert ("login", "reader-box@example.test", "app-password") in FakeSMTP.log


def test_the_alert_never_carries_the_password_or_the_sign_in():
    response = _sign_in(_client())
    text = FakeSMTP.sent[0].as_string()
    assert TEST_PASSWORD not in text
    cookie = response.headers["set-cookie"].split("=")[1].split(";")[0]
    assert cookie not in text


def test_one_wrong_password_sends_nothing():
    _sign_in(_client(), "nope")
    assert FakeSMTP.sent == []


def test_a_lockout_is_emailed_once_when_it_starts():
    client = _client()
    for _ in range(auth.LOCK_AFTER + 3):
        _sign_in(client, "nope", **{"Fly-Client-IP": "203.0.113.9"})
    (message,) = FakeSMTP.sent
    assert "locked" in message["Subject"].lower()
    assert "203.0.113.9" in message.get_content()


def test_a_sign_in_that_fails_sends_no_sign_in_alert():
    _sign_in(_client(), "nope")
    assert not any("new sign-in" in m["Subject"].lower() for m in FakeSMTP.sent)


def test_without_an_alert_address_nothing_is_sent_and_sign_in_works(monkeypatch):
    monkeypatch.delenv("ALERT_EMAIL")
    assert _sign_in(_client()).status_code == 303
    assert FakeSMTP.sent == []


def test_without_the_mailbox_nothing_is_sent_and_sign_in_works(monkeypatch):
    monkeypatch.delenv("MAIL_IMAP_PASSWORD")
    assert _sign_in(_client()).status_code == 303
    assert FakeSMTP.sent == []


def test_a_mail_server_that_fails_never_blocks_signing_in_and_is_noted():
    FakeSMTP.fail = True
    client = _client()
    assert _sign_in(client).status_code == 303
    assert client.get("/", headers={"Sec-Fetch-Mode": "navigate"}).status_code == 200
    failed = [e for e in diag.snapshot()["events"] if e["e"] == "alert-failed"]
    assert len(failed) == 1
    assert "mail server down" in failed[0]["d"]


def test_the_sending_host_comes_from_the_receiving_one_unless_told(monkeypatch):
    assert alert_config().host == "smtp.example.test"
    monkeypatch.setenv("MAIL_SMTP_HOST", "mail.elsewhere.test")
    assert alert_config().host == "mail.elsewhere.test"
    monkeypatch.setenv("MAIL_IMAP_HOST", "imap.gmail.com")
    monkeypatch.delenv("MAIL_SMTP_HOST")
    assert alert_config().host == "smtp.gmail.com"
