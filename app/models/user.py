from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = "user"

    userId = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="student")
    phoneNumber = db.Column(db.String(20))
    address = db.Column(db.String(255))
    profile_image = db.Column(db.Text, nullable=True)  # stores base64 data URL or filename

    # For Password Reset (OTP)
    otp_code = db.Column(db.String(6), nullable=True)
    otp_expiry = db.Column(db.DateTime, nullable=True)

    # Account activation
    is_active = db.Column(db.Boolean, default=True)
    activation_token = db.Column(db.String(100), nullable=True)

    # For RBAC (Specific Faculty Access)
    # Stores as: "view_activities,view_placement,post_announcement"
    permissions = db.Column(db.String(255), default="")

    def set_password(self, password):
        """Hashes the password before storing it."""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Verifies the hashed password."""
        return check_password_hash(self.password, password)

    def get_permissions_list(self):
        """Returns the permissions string as a clean Python list for JS."""
        if not self.permissions:
            return []
        
        return [p.strip() for p in self.permissions.split(',') if p.strip()]

    def to_dict(self):
        """Helper to convert user object to dictionary for JSON responses."""
        return {
            "userId": self.userId,
            "name": self.name,
            "email": self.email,
            "role": self.role,
            "permissions": self.get_permissions_list()
        }