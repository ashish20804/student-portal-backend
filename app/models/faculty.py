from app.extensions import db

class Faculty(db.Model):
    __tablename__ = "faculty"

    userId = db.Column(
        db.Integer,
        db.ForeignKey("user.userId"),
        primary_key=True
    )

    designation = db.Column(db.String(50))
    department = db.Column(db.String(50))
