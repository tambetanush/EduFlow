from __future__ import annotations

import smtplib
from email.message import EmailMessage

from app.config import settings


def send_email(*, to_email: str, subject: str, body: str) -> None:
    host = settings.SMTP_HOST.strip()
    from_email = settings.SMTP_FROM_EMAIL.strip()
    if not host or not from_email:
        return

    msg = EmailMessage()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP(host, settings.SMTP_PORT, timeout=10) as smtp:
        if settings.SMTP_USE_TLS:
            smtp.starttls()
        username = settings.SMTP_USERNAME.strip()
        if username:
            smtp.login(username, settings.SMTP_PASSWORD)
        smtp.send_message(msg)

