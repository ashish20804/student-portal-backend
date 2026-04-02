from app.extensions import db
from datetime import date

class CommitteeMembership(db.Model):
    __tablename__ = "committeemembership"

    membershipId = db.Column(db.Integer, primary_key=True, autoincrement=True)

    userId = db.Column(
        db.Integer,
        db.ForeignKey("user.userId", ondelete="CASCADE"),
        nullable=False
    )

    committeeCode = db.Column(
        db.Integer,
        db.ForeignKey("committee.committeeCode", ondelete="CASCADE"),
        nullable=False
    )

    role = db.Column(db.String(50), default="Member")
    joinDate = db.Column(db.Date, default=date.today)

    __table_args__ = (
        db.UniqueConstraint('userId', 'committeeCode', name='unique_user_committee'),
    )
