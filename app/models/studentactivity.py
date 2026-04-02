from app.extensions import db

class StudentActivity(db.Model):
    __tablename__ = "studentactivity"

    studentActivityId = db.Column(db.Integer, primary_key=True, autoincrement=True)

    userId = db.Column(
        db.Integer,
        db.ForeignKey("user.userId", ondelete="CASCADE"),
        nullable=False
    )

    activityId = db.Column(
        db.Integer,
        db.ForeignKey("activity.activityId", ondelete="CASCADE"),
        nullable=False
    )

    __table_args__ = (
        db.UniqueConstraint('userId', 'activityId', name='unique_user_activity'),
    )
