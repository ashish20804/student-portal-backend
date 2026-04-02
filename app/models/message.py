from app.extensions import db
from datetime import datetime

class Message(db.Model):
    __tablename__ = "message"

    messageId = db.Column(db.Integer, primary_key=True)

    senderId = db.Column(
        db.Integer,
        db.ForeignKey("user.userId", ondelete="CASCADE"),
        nullable=False
    )

    receiverId = db.Column(
        db.Integer,
        db.ForeignKey("user.userId", ondelete="CASCADE"),
        nullable=False
    )

    content = db.Column(db.Text, nullable=False)

    timestamp = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # Relationships
    sender = db.relationship(
        "User",
        foreign_keys=[senderId],
        backref="sent_messages"
    )

    receiver = db.relationship(
        "User",
        foreign_keys=[receiverId],
        backref="received_messages"
    )

    