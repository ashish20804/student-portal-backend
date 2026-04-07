"""
email_utils.py

On Render : Brevo HTTP API (HTTPS port 443 — works on Render free tier)
Locally   : Gmail SMTP (works on local machine)

Render env vars needed:
    BREVO_API_KEY  = your_brevo_api_key
    MAIL_USER      = abhedi16@gmail.com
    FRONTEND_URL   = https://student-portal-backend-8icb.onrender.com
"""

import os
import json
import urllib.request
import urllib.error
from flask import current_app
from flask_mail import Message
from app.extensions import mail


def _send_via_brevo(to_email: str, to_name: str, subject: str, body: str):
    """Send via Brevo HTTP API — works on Render (HTTPS port 443)."""
    api_key      = os.getenv("BREVO_API_KEY", "")
    sender_email = os.getenv("MAIL_USER", "abhedi16@gmail.com")

    payload = json.dumps({
        "sender":      {"name": "Student Portal", "email": sender_email},
        "to":          [{"email": to_email, "name": to_name}],
        "subject":     subject,
        "textContent": body
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.brevo.com/v3/smtp/email",
        data=payload,
        headers={
            "api-key":      api_key,
            "Content-Type": "application/json"
        },
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=15) as resp:
        result = resp.read()
        print(f"[Email] Brevo success for {to_email}: {result}")


def _send_via_flask_mail(to_email: str, subject: str, body: str):
    """Send via Gmail SMTP — used locally."""
    msg = Message(subject, recipients=[to_email])
    msg.body = body
    mail.send(msg)
    print(f"[Email] Gmail SMTP success for {to_email}")


def send_email_async(to_email: str, to_name: str, subject: str, body: str):
    """
    Send email synchronously.
    Uses Brevo if BREVO_API_KEY is set (Render), else Gmail SMTP (local).
    """
    brevo_key = os.getenv("BREVO_API_KEY", "")

    try:
        print(f"[Email] Sending to {to_email} via {'Brevo' if brevo_key else 'Gmail SMTP'}...")
        if brevo_key:
            _send_via_brevo(to_email, to_name, subject, body)
        else:
            _send_via_flask_mail(to_email, subject, body)
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        print(f"[Email] Brevo HTTP error {e.code} for {to_email}: {error_body}")
    except Exception as e:
        print(f"[Email] FAILED for {to_email}: {type(e).__name__}: {e}")
