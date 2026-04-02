from app.extensions import db

class Committee(db.Model):
    __tablename__ = "committee"

    committeeCode = db.Column(db.Integer, primary_key=True, autoincrement=True)
    committeeName = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50))
