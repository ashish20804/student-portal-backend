from app.extensions import db

class HigherStudies(db.Model):
    __tablename__ = "higherstudies"

    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey("user.userId"), nullable=False)

    university = db.Column(db.String(150))
    country = db.Column(db.String(100))
    courseName = db.Column(db.String(150))
    applicationDate = db.Column(db.Date)
    admissionStatus = db.Column(db.String(50))
    # New Column for Admission Letter PDF
    proof_path = db.Column(db.String(255), nullable=True) 

    user = db.relationship(
        "User",
        backref=db.backref("higher_studies_applications", lazy=True)
    )