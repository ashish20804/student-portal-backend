from app import create_app
from app.extensions import db
from app.models.user import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    user = User(
        name="Test User",
        email="test@example.com",
        password=generate_password_hash("1234"),
        role="student"
    )

    db.session.add(user)
    db.session.commit()

    print("User created successfully!")
