"""
Run this script to create the admin user in the database.
Works for both local MySQL and Railway (set env vars before running).

Local usage:
    python create_admin.py

Railway usage (set these env vars first or put them in .env):
    DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME
"""

from app import create_app
from app.extensions import db
from app.models.user import User

ADMIN_EMAIL    = "admin@studentportal.com"
ADMIN_PASSWORD = "Admin@1234"
ADMIN_NAME     = "System Administrator"

app = create_app()

with app.app_context():
    existing = User.query.filter_by(email=ADMIN_EMAIL).first()
    if existing:
        # Update role and reset password in case it was wrong
        existing.role      = "admin"
        existing.is_active = True
        existing.activation_token = None
        existing.set_password(ADMIN_PASSWORD)
        db.session.commit()
        print(f"Admin already exists — password reset to: {ADMIN_PASSWORD}")
    else:
        admin = User(
            name=ADMIN_NAME,
            email=ADMIN_EMAIL,
            role="admin",
            is_active=True
        )
        admin.set_password(ADMIN_PASSWORD)
        db.session.add(admin)
        db.session.commit()
        print(f"Admin created successfully!")

    print(f"\nLogin credentials:")
    print(f"  Email   : {ADMIN_EMAIL}")
    print(f"  Password: {ADMIN_PASSWORD}")
    print(f"\nChange the password after first login!")
