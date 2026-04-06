"""
email_utils.py

On Render  : uses Resend HTTP API (HTTPS port 443 — always works on Render)
Locally    : uses Gmail SMTP via smtplib

Render Environment Variables needed:
    RESEND_API_KEY  = re_your_key_here
    RESEND_FROM     = onboarding@resend.dev   (or your verified sender)
    FRONTEND_URL    = https://student-portal-backend-8icb.onrender.com
"""

import os
import io
import smtplib
import threading
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def _send_via_resend(to_email: str, to_name: str, subject: str, body: str):
    """Send via Resend HTTP API — works on Render (HTTPS port 443)."""
    api_key      = os.getenv("RESEND_API_KEY", "")
    sender_email = os.getenv("RESEND_FROM", "onboarding@resend.dev")

    resp = requests.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type":  "application/json"
        },
        json={
            "from":    f"Student Portal <{sender_email}>",
            "to":      [to_email],
            "subject": subject,
            "text":    body
        },
        timeout=15
    )
    resp.raise_for_status()
    print(f"[Resend] Email sent to {to_email}")


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
    Uses Resend API if RESEND_API_KEY is set (Render), else Gmail SMTP (local).
    """
    from flask import current_app
    app        = current_app._get_current_object()
    resend_key = os.getenv("RESEND_API_KEY", "")

    def _run():
        with app.app_context():
            try:
                if resend_key:
                    _send_via_resend(to_email, to_name, subject, body)
                else:
                    _send_via_smtp(to_email, subject, body)
            except Exception as e:
                print(f"[Email] Failed for {to_email}: {e}")

    threading.Thread(target=_run, daemon=True).start()
