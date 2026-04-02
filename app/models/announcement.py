from app.extensions import db
from datetime import datetime

class Announcement(db.Model):
    __tablename__ = "announcement"

    id        = db.Column(db.Integer, primary_key=True)
    content   = db.Column(db.Text, nullable=False)
    posted_by = db.Column(db.Integer, db.ForeignKey("user.userId", ondelete="CASCADE"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    author = db.relationship("User", backref=db.backref("announcements", lazy=True))
