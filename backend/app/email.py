import logging
import smtplib
import time
from dataclasses import dataclass
from email.message import EmailMessage as MIMEEmailMessage
from typing import Protocol

from app.config import Settings, get_settings


logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TransactionalEmail:
    recipient: str
    subject: str
    text_body: str
    sender: str = "no-reply@recipe.local"


class TransactionalEmailSender(Protocol):
    def send(self, message: TransactionalEmail) -> None:
        """Deliver a transactional email or raise EmailDeliveryError."""


class EmailDeliveryError(RuntimeError):
    """Raised when an email cannot be delivered."""


class SmtpEmailSender:
    def __init__(self, settings: Settings | None = None, timeout_seconds: float = 10) -> None:
        self._settings = settings or get_settings()
        self._timeout_seconds = timeout_seconds

    def send(self, message: TransactionalEmail) -> None:
        mime_message = MIMEEmailMessage()
        mime_message["From"] = message.sender
        mime_message["To"] = message.recipient
        mime_message["Subject"] = message.subject
        mime_message.set_content(message.text_body)

        for attempt in range(3):
            try:
                with smtplib.SMTP(
                    self._settings.mailpit_smtp_host,
                    self._settings.mailpit_smtp_port,
                    timeout=self._timeout_seconds,
                ) as smtp:
                    refused = smtp.send_message(mime_message)
            except (OSError, smtplib.SMTPException) as exc:
                if attempt == 2:
                    logger.warning("Transactional email delivery failed via SMTP")
                    raise EmailDeliveryError("Transactional email delivery failed via SMTP") from exc
                time.sleep(0.25 * (2**attempt))
                continue

            if refused:
                logger.warning("Transactional email delivery failed: SMTP recipient refused")
                raise EmailDeliveryError("SMTP server refused the transactional email recipient")

            logger.info("Transactional email delivered via SMTP")
            return