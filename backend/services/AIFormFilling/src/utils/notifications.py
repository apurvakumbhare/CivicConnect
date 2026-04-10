import os
import smtplib
import ssl
import logging
import asyncio
from email.message import EmailMessage
from typing import Dict, Any

logger = logging.getLogger(__name__)

class AIFormNotificationService:
    """Service to notify citizens when their grievance is submitted."""
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587")) if os.getenv("SMTP_PORT") else None
        self.smtp_user = os.getenv("SMTP_USERNAME")
        self.smtp_pass = os.getenv("SMTP_PASSWORD")
        self.smtp_from = os.getenv("SMTP_FROM", self.smtp_user)
        self.smtp_use_ssl = os.getenv("SMTP_USE_SSL", "false").lower() in ("1", "true", "yes")
        self.smtp_starttls = os.getenv("SMTP_STARTTLS", "true").lower() in ("1", "true", "yes")

    async def send_ticket_email(self, to_email: str, form_id: str, form_data: Dict[str, Any]) -> bool:
        """Send a submission confirmation email with ticket id and short summary."""
        subject = f"Your grievance has been submitted — Reference ID: {form_id}"
        # Build a short summary: pick a few meaningful keys if present
        summary_keys = ["title", "category", "description", "address", "status"]
        summary_lines = []
        for k in summary_keys:
            if k in form_data and form_data[k]:
                summary_lines.append(f"{k.capitalize()}: {form_data[k]}")
        # Fallback to a compact JSON snippet if nothing obvious found
        if not summary_lines:
            try:
                import json
                compact = json.dumps({k: form_data.get(k) for k in list(form_data)[:5]}, ensure_ascii=False)
            except Exception:
                compact = "<summary unavailable>"
            summary_lines = [compact]

        body = f"""Dear Citizen,

Your grievance has been submitted successfully.

Reference ID: {form_id}

Summary:
{chr(10).join(summary_lines)}

You can use the Reference ID to track the status of your grievance.

Best regards,
Government Portal Team
"""

        summary_html = ""
        for line in summary_lines:
            if ':' in line:
                key, val = line.split(":", 1)
                summary_html += f'<div class="summary-item"><strong>{key.strip()}:</strong> {val.strip()}</div>'
            else:
                summary_html += f'<div class="summary-item">{line}</div>'

        html_body = f"""
        <html>
            <head>
                <style>
                    body {{ font-family: 'Inter', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f8fafc; margin: 0; padding: 0; color: #334155; }}
                    .container {{ max-width: 600px; margin: 40px auto; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 10px 25px rgba(0,0,0,0.05); }}
                    .header {{ background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%); color: white; text-align: center; padding: 30px 20px; }}
                    .header h1 {{ margin: 0; font-size: 24px; font-weight: 700; letter-spacing: -0.5px; }}
                    .content {{ padding: 40px 30px; }}
                    .greeting {{ font-size: 18px; font-weight: 600; margin-bottom: 20px; color: #0f172a; }}
                    .success-msg {{ background-color: #ecfdf5; color: #065f46; padding: 15px; border-radius: 8px; margin-bottom: 30px; font-weight: 500; border-left: 4px solid #10b981; }}
                    .ticket-details {{ background-color: #f1f5f9; border-radius: 10px; padding: 25px; margin-bottom: 30px; }}
                    .ticket-label {{ font-size: 12px; text-transform: uppercase; letter-spacing: 1px; color: #64748b; margin-bottom: 5px; display: block; }}
                    .ticket-id {{ font-size: 22px; font-family: monospace; font-weight: 700; color: #1e293b; margin-bottom: 20px; display: block; word-break: break-all; }}
                    .summary-item {{ margin-bottom: 8px; font-size: 15px; line-height: 1.5; }}
                    .footer {{ text-align: center; padding: 20px; font-size: 13px; color: #94a3b8; background-color: #f8fafc; border-top: 1px solid #e2e8f0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>CivicConnect Support</h1>
                    </div>
                    <div class="content">
                        <div class="greeting">Dear Citizen,</div>
                        <div class="success-msg">
                            &#10003; Your grievance has been submitted successfully
                        </div>
                        
                        <div class="ticket-details">
                            <span class="ticket-label">Reference ID</span>
                            <span class="ticket-id">{form_id}</span>
                            
                            <span class="ticket-label" style="margin-top: 15px; margin-bottom: 10px;">Summary of Details</span>
                            {summary_html}
                        </div>
                        
                        <p style="color: #475569; line-height: 1.6;">
                            We are dynamically routing your request. You can use your Reference ID to track the real-time status of your grievance through the portal.
                        </p>
                    </div>
                    <div class="footer">
                        &copy; Government Portal Team - CivicConnect
                    </div>
                </div>
            </body>
        </html>
        """

        if not self.smtp_host or not self.smtp_port:
            logger.warning("SMTP config missing for AIFormFilling service; using simulated send")
            logger.info(f"Simulated ticket email to {to_email}: {subject}")
            await asyncio.sleep(0.1)
            return True

        msg = EmailMessage()
        msg["From"] = self.smtp_from or self.smtp_user or "no-reply@example.com"
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.set_content(body)
        msg.add_alternative(html_body, subtype='html')

        def _send():
            if self.smtp_use_ssl:
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port, context=context) as s:
                    if self.smtp_user and self.smtp_pass:
                        s.login(self.smtp_user, self.smtp_pass)
                    s.send_message(msg)
            else:
                with smtplib.SMTP(self.smtp_host, self.smtp_port) as s:
                    s.ehlo()
                    if self.smtp_starttls:
                        context = ssl.create_default_context()
                        s.starttls(context=context)
                        s.ehlo()
                    if self.smtp_user and self.smtp_pass:
                        s.login(self.smtp_user, self.smtp_pass)
                    s.send_message(msg)
            return True

        try:
            await asyncio.to_thread(_send)
            logger.info(f"Ticket email sent to {to_email} for form {form_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to send ticket email to {to_email} for form {form_id}: {e}")
            return False

ai_notification_service = AIFormNotificationService()
