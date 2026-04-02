from app.extensions import db

class Student(db.Model):
    __tablename__ = "student"

    userId = db.Column(
        db.Integer,
        db.ForeignKey("user.userId"),
        primary_key=True
    )

    rollNumber = db.Column(db.String(20), unique=True, nullable=False)
    program = db.Column(db.String(50))
    semester = db.Column(db.Integer)   # ✅ FIXED
    department = db.Column(db.String(50))

    sgpa = db.Column(db.Float, default=0.0)
    cgpa = db.Column(db.Float, default=0.0)
    attendance_percentage = db.Column(db.Float, default=0.0)

    isPlanningHigherStudies = db.Column(db.Boolean, default=False)

    user = db.relationship("User", backref=db.backref("student_profile", uselist=False))

