"""
email_utils.py

On Render  : uses Brevo HTTP API (HTTPS port 443 — always works on Render)
Locally    : uses Gmail SMTP via smtplib (as before)

Render Environment Variables needed:
    BREVO_API_KEY  = your_brevo_api_key
    BREVO_FROM     = your_verified_sender@email.com  (verified in Brevo dashboard)
    FRONTEND_URL   = https://student-portal-backend-8icb.onrender.com
"""

import os
import smtplib
import threading
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def _send_via_brevo(to_email: str, to_name: str, subject: str, body: str):
    """Send via Brevo HTTP API — works on Render (HTTPS port 443)."""
    api_key      = os.getenv("BREVO_API_KEY", "")
    sender_email = os.getenv("BREVO_FROM", os.getenv("MAIL_USER", ""))
    sender_name  = "Student Portal Admin"

    resp = requests.post(
        "https://api.brevo.com/v3/smtp/email",
        headers={
            "api-key":      api_key,
            "Content-Type": "application/json"
        },
        json={
            "sender":      {"name": sender_name, "email": sender_email},
            "to":          [{"email": to_email, "name": to_name}],
            "subject":     subject,
            "textContent": body
        },
        timeout=15
    )
    resp.raise_for_status()
    print(f"[Brevo] Email sent to {to_email}")


def _send_via_smtp(to_email: str, subject: str, body: str):
    """Send via Gmail SMTP — used locally where SMTP ports are open."""
    smtp_user = os.getenv("MAIL_USER", "")
    smtp_pass = os.getenv("MAIL_PASS", "")

    msg = MIMEMultipart()
    msg['From']    = f"Student Portal Admin <{smtp_user}>"
    msg['To']      = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=20) as s:
            s.login(smtp_user, smtp_pass)
            s.sendmail(smtp_user, to_email, msg.as_string())
        print(f"[SMTP 465] Email sent to {to_email}")
        return
    except Exception:
        pass

    with smtplib.SMTP('smtp.gmail.com', 587, timeout=20) as s:
        s.ehlo()
        s.starttls()
        s.login(smtp_user, smtp_pass)
        s.sendmail(smtp_user, to_email, msg.as_string())
    print(f"[SMTP 587] Email sent to {to_email}")


def send_email_async(to_email: str, to_name: str, subject: str, body: str):
    """
    Send email in a background thread.
    Uses Brevo API if BREVO_API_KEY is set (Render), else Gmail SMTP (local).
    """
    from flask import current_app
    app        = current_app._get_current_object()
    brevo_key  = os.getenv("BREVO_API_KEY", "")

    def _run():
        with app.app_context():
            try:
                if brevo_key:
                    _send_via_brevo(to_email, to_name, subject, body)
                else:
                    _send_via_smtp(to_email, subject, body)
            except Exception as e:
                print(f"[Email] Failed for {to_email}: {e}")

    threading.Thread(target=_run, daemon=True).start()
