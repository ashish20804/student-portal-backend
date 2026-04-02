from app.extensions import db

class Placement(db.Model):
    __tablename__ = "placement"

    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey("user.userId"), nullable=False)

    companyName = db.Column(db.String(100))
    jobRole = db.Column(db.String(100))
    package = db.Column(db.String(50))
    status = db.Column(db.String(30))  # Selected / Not Selected
    placementYear = db.Column(db.Integer)
    # New Column for Offer Letter PDF
    proof_path = db.Column(db.String(255), nullable=True) 

    created_at = db.Column(db.DateTime, server_default=db.func.now())

    user = db.relationship(
        "User",
        backref=db.backref("placements", lazy=True)
    )