"""
Run this once to add activation columns to the user table:
    python migrate_activation.py
"""
from app import create_app
from app.extensions import db

app = create_app()
with app.app_context():
    with db.engine.connect() as conn:
        try:
            conn.execute(db.text("ALTER TABLE user ADD COLUMN is_active TINYINT(1) NOT NULL DEFAULT 1"))
            print("✅ Added is_active column")
        except Exception as e:
            print(f"⚠️  is_active: {e}")

        try:
            conn.execute(db.text("ALTER TABLE user ADD COLUMN activation_token VARCHAR(100) NULL"))
            print("✅ Added activation_token column")
        except Exception as e:
            print(f"⚠️  activation_token: {e}")

        conn.commit()
    print("✅ Migration complete. All existing users remain active.")
