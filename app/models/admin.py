from app.extensions import db

class Admin(db.Model):
    __tablename__ = "admin"

    userId = db.Column(
        db.Integer,
        db.ForeignKey("user.userId"),
        primary_key=True
    )

    adminLevel = db.Column(db.String(20))

    user = db.relationship("User", backref="admin_profile")
