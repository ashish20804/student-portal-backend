"""
email_utils.py — Synchronous email sending.

Sends email BEFORE returning the HTTP response so Render worker restarts
cannot kill the email mid-send.

Uses port 465 SSL (works on Render) with fallback to port 587 TLS.
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email_async(to_email: str, to_name: str, subject: str, body: str):
    """
    Send email synchronously using smtplib.
    Named 'async' for API compatibility but runs inline.
    Port 465 SSL tried first (works on Render), then 587 TLS fallback.
    """
    smtp_user = os.getenv("MAIL_USER", "")
    smtp_pass = os.getenv("MAIL_PASS", "")

    if not smtp_user or not smtp_pass:
        print(f"[Email] Skipped — MAIL_USER or MAIL_PASS not set")
        return

    msg = MIMEMultipart()
    msg['From']    = f"Student Portal Admin <{smtp_user}>"
    msg['To']      = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Try port 465 SSL first
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=20) as server:
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, to_email, msg.as_string())
        print(f"[SMTP SSL 465] Email sent to {to_email}")
        return
    except Exception as e465:
        print(f"[SMTP SSL 465] Failed: {e465} — trying TLS 587...")

    # Fallback: port 587 TLS
    try:
        with smtplib.SMTP('smtp.gmail.com', 587, timeout=20) as server:
            server.ehlo()
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, to_email, msg.as_string())
        print(f"[SMTP TLS 587] Email sent to {to_email}")
    except Exception as e587:
        print(f"[SMTP TLS 587] Failed: {e587}")
        print(f"[Email] All methods failed for {to_email}")
