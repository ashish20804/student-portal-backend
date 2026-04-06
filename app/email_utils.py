"""
email_utils.py — Flask-Mail based email sending via Gmail SSL port 465.
"""

import threading
from flask import current_app
from flask_mail import Message
from app.extensions import mail


def send_email_async(to_email: str, to_name: str, subject: str, body: str):
    """Send email in a background thread using Flask-Mail."""
    app = current_app._get_current_object()

    def _run():
        with app.app_context():
            try:
                print(f"[Email] Attempting to send to {to_email}...")
                msg = Message(subject, recipients=[to_email])
                msg.body = body
                mail.send(msg)
                print(f"[Email] Successfully sent to {to_email}")
            except Exception as e:
                print(f"[Email] FAILED for {to_email}: {type(e).__name__}: {e}")

    threading.Thread(target=_run, daemon=True).start()
    print(f"[Email] Background thread started for {to_email}")
