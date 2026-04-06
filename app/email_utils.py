"""
email_utils.py — Simple Flask-Mail based email sending.

Uses the original working approach (Flask-Mail with Gmail SMTP).
The only change from the original code is FRONTEND_URL is now dynamic
so activation links work on both local and Render.

Required environment variables:
    MAIL_USER    = 22bce024@nirmauni.ac.in
    MAIL_PASS    = haoh ffxs beay fmav
    FRONTEND_URL = http://127.0.0.1:8000          (local .env)
    FRONTEND_URL = https://student-portal-backend-8icb.onrender.com  (Render dashboard)
"""

import threading
from flask import current_app
from flask_mail import Message
from app.extensions import mail


def send_email_async(to_email: str, to_name: str, subject: str, body: str):
    """Send email in a background thread using Flask-Mail (original working method)."""
    app = current_app._get_current_object()

    def _run():
        with app.app_context():
            try:
                msg = Message(subject, recipients=[to_email])
                msg.body = body
                mail.send(msg)
                print(f"[Email] Sent to {to_email}")
            except Exception as e:
                print(f"[Email] Failed for {to_email}: {e}")

    threading.Thread(target=_run, daemon=True).start()
