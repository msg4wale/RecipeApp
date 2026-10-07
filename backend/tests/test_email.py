import json
import logging
import os
import smtplib
import time
from email.message import EmailMessage as MIMEEmailMessage
from urllib.error import URLError
from urllib.request import urlopen
from uuid import uuid4

import pytest

from app.config import Settings
from app.email import EmailDeliveryError, SmtpEmailSender, TransactionalEmail


class FakeSMTP:
    instances: list["FakeSMTP"] = []

    def __init__(self, host: str, port: int, timeout: float) -> None:
        self.host = host
        self.port = port
        self.timeout = timeout
        self.message: MIMEEmailMessage | None = None
        self.__class__.instances.append(self)

    def __enter__(self) -> "FakeSMTP":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def send_message(self, message: MIMEEmailMessage) -> dict[str, tuple[int, bytes]]:
        self.message = message
        return {}


def test_smtp_sender_constructs_and_delivers_message(monkeypatch: pytest.MonkeyPatch) -> None:
    FakeSMTP.instances.clear()
    monkeypatch.setattr("app.email.smtplib.SMTP", FakeSMTP)
    settings = Settings(mailpit_smtp_host="mailpit.test", mailpit_smtp_port=2525)
    message = TransactionalEmail(
        recipient="chef@example.com",
        subject="Verify your email",
        text_body="Use the link to verify your account.",
    )

    SmtpEmailSender(settings, timeout_seconds=3).send(message)

    smtp = FakeSMTP.instances[0]
    assert (smtp.host, smtp.port, smtp.timeout) == ("mailpit.test", 2525, 3)
    assert smtp.message is not None
    assert smtp.message["From"] == "no-reply@recipe.local"
    assert smtp.message["To"] == "chef@example.com"
    assert smtp.message["Subject"] == "Verify your email"
    assert smtp.message.get_content() == "Use the link to verify your account.\n"


def test_smtp_sender_raises_clear_error_without_logging_message_content(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    attempts = 0

    def fail_connect(*args: object, **kwargs: object) -> None:
        nonlocal attempts
        attempts += 1
        raise OSError("connection refused")

    monkeypatch.setattr("app.email.smtplib.SMTP", fail_connect)
    monkeypatch.setattr("app.email.time.sleep", lambda delay: None)
    message = TransactionalEmail(
        recipient="private@example.com",
        subject="Secret subject",
        text_body="Sensitive verification token",
    )

    with caplog.at_level(logging.INFO), pytest.raises(EmailDeliveryError, match="delivery failed"):
        SmtpEmailSender(Settings()).send(message)

    assert "delivery failed via SMTP" in caplog.text
    assert attempts == 3
    assert "private@example.com" not in caplog.text
    assert "Secret subject" not in caplog.text
    assert "Sensitive verification token" not in caplog.text


def test_smtp_sender_treats_recipient_refusal_as_delivery_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    class RefusingSMTP(FakeSMTP):
        def send_message(self, message: MIMEEmailMessage) -> dict[str, tuple[int, bytes]]:
            return {"chef@example.com": (550, b"rejected")}

    monkeypatch.setattr("app.email.smtplib.SMTP", RefusingSMTP)

    with pytest.raises(EmailDeliveryError, match="refused"):
        SmtpEmailSender(Settings()).send(
            TransactionalEmail("chef@example.com", "Decision", "Your application was reviewed.")
        )


def test_smtp_sender_retries_transient_failure_with_exponential_backoff(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    delays: list[float] = []

    class IntermittentSMTP(FakeSMTP):
        attempts = 0

        def send_message(self, message: MIMEEmailMessage) -> dict[str, tuple[int, bytes]]:
            self.__class__.attempts += 1
            if self.__class__.attempts < 3:
                raise smtplib.SMTPServerDisconnected("temporary failure")
            return {}

    monkeypatch.setattr("app.email.smtplib.SMTP", IntermittentSMTP)
    monkeypatch.setattr("app.email.time.sleep", delays.append)

    SmtpEmailSender(Settings()).send(
        TransactionalEmail("chef@example.com", "Decision", "Your application was reviewed.")
    )

    assert IntermittentSMTP.attempts == 3
    assert delays == [0.25, 0.5]


def _mailpit_messages(api_url: str) -> list[dict[str, object]]:
    with urlopen(api_url, timeout=2) as response:
        payload = json.load(response)
    return payload["messages"]


def test_mailpit_inbox_receives_transactional_email() -> None:
    if os.getenv("RUN_MAILPIT_INTEGRATION") != "1":
        pytest.skip("set RUN_MAILPIT_INTEGRATION=1 to run the Mailpit integration check")

    api_url = os.getenv("MAILPIT_API_URL", "http://localhost:8025/api/v1/messages")
    try:
        _mailpit_messages(api_url)
    except (OSError, URLError, TimeoutError, json.JSONDecodeError):
        pytest.skip("Mailpit inbox API is unavailable")

    subject = f"Integration check {uuid4()}"
    SmtpEmailSender().send(
        TransactionalEmail(
            recipient="mailpit-check@example.com",
            subject=subject,
            text_body="Mailpit delivery integration check.",
        )
    )

    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        if any(message.get("Subject") == subject for message in _mailpit_messages(api_url)):
            return
        time.sleep(0.25)

    pytest.fail("Email did not appear in the Mailpit inbox before the timeout")