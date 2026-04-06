"""
email_utils.py — Shared email sending utility.

Uses Python smtplib with SSL on port 465 (works on most hosts including Render).
Falls back to Flask-Mail if smtplib fails.
No external API accounts needed.
"""

import os
import smtplib
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import current_app


def _send_via_smtplib(to_email: str, to_name: str, subject: str, body: str,
                       smtp_user: str, smtp_pass: str):
    """
    Send via Python smtplib — tries port 465 (SSL) first, then 587 (TLS).
    Both use the same Gmail credentials.
    """
    msg = MIMEMultipart()
    msg['From']    = f"Student Portal Admin <{smtp_user}>"
    msg['To']      = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Try port 465 SSL first (often allowed on Render)
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=20) as server:
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, to_email, msg.as_string())
        print(f"[SMTP SSL 465] Email sent to {to_email}")
        return
    except Exception as e465:
        print(f"[SMTP SSL 465] Failed: {e465} — trying TLS 587...")

    # Fallback: port 587 TLS
    with smtplib.SMTP('smtp.gmail.com', 587, timeout=20) as server:
        server.ehlo()
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_user, to_email, msg.as_string())
    print(f"[SMTP TLS 587] Email sent to {to_email}")


def send_email_async(to_email: str, to_name: str, subject: str, body: str):
    """
    Send an email in a background thread so it never blocks the HTTP response.
    Uses Gmail credentials from environment variables.
    """
    app         = current_app._get_current_object()
    smtp_user   = os.getenv("MAIL_USER", "")
    smtp_pass   = os.getenv("MAIL_PASS", "")

    def _run():
        try:
            if smtp_user and smtp_pass:
                _send_via_smtplib(to_email, to_name, subject, body, smtp_user, smtp_pass)
            else:
                # Flask-Mail fallback (local dev without env vars)
                from flask_mail import Message
                from app.extensions import mail
                with app.app_context():
                    msg = Message(subject, recipients=[to_email])
                    msg.body = body
                    mail.send(msg)
                print(f"[Flask-Mail] Email sent to {to_email}")
        except Exception as e:
            print(f"[Email] Failed for {to_email}: {e}")

    threading.Thread(target=_run, daemon=True).start()
