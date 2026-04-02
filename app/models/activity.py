from app.extensions import db

class Activity(db.Model):
    __tablename__ = "activity"

    activityId = db.Column(db.Integer, primary_key=True, autoincrement=True)
    activityName = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50))
    level = db.Column(db.String(30))
    achievement = db.Column(db.String(100))
    # New Column for PDF Proof (Certificate/Paper)
    proof_path = db.Column(db.String(255), nullable=True) 

    def __repr__(self):
        return f"<Activity {self.activityName}>"