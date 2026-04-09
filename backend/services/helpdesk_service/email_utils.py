import os
import smtplib
import ssl
import logging
import asyncio
from email.message import EmailMessage

logger = logging.getLogger(__name__)


async def send_helpdesk_email(name: str, sender_email: str, message: str) -> bool:
    """
    Send the user's contact form message to the organization helpdesk email.
    Uses SMTP credentials from environment variables.
    """
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port_str = os.getenv("SMTP_PORT", "587")
    smtp_user = os.getenv("SMTP_USERNAME")
    smtp_pass = os.getenv("SMTP_PASSWORD")
    smtp_from = os.getenv("SMTP_FROM", smtp_user)
    smtp_starttls = os.getenv("SMTP_STARTTLS", "true").lower() in ("1", "true", "yes")
    helpdesk_email = os.getenv("HELPDESK_EMAIL", smtp_user)

    if not smtp_host or not smtp_user or not smtp_pass:
        logger.error("SMTP configuration is incomplete. Cannot send helpdesk email.")
        return False

    smtp_port = int(smtp_port_str)

    subject = f"[CivicConnect Helpdesk] New message from {name}"
    body = f"""You have received a new message from the CivicConnect portal contact form.

From: {name}
Email: {sender_email}

Message:
{message}

---
This email was sent automatically by the CivicConnect Grievance Redressal System.
"""

    msg = EmailMessage()
    msg["From"] = smtp_from
    msg["To"] = helpdesk_email
    msg["Reply-To"] = sender_email
    msg["Subject"] = subject
    msg.set_content(body)

    def _send():
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.ehlo()
            if smtp_starttls:
                context = ssl.create_default_context()
                server.starttls(context=context)
                server.ehlo()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        return True

    try:
        await asyncio.to_thread(_send)
        logger.info(f"Helpdesk email sent to {helpdesk_email} from {sender_email}")
        return True
    except Exception as e:
        logger.error(f"Failed to send helpdesk email: {e}")
        raise
