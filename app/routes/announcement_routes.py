from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.announcement import Announcement
from app.models.user import User

announcement_bp = Blueprint("announcement_bp", __name__, url_prefix="/announcements")


@announcement_bp.route("", methods=["POST"])
@jwt_required()
def post_announcement():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user or user.role not in ("admin", "faculty"):
        return jsonify({"message": "Not authorized"}), 403

    # Faculty must have post_announcement permission
    if user.role == "faculty":
        perms = user.get_permissions_list()
        if "post_announcement" not in perms:
            return jsonify({"message": "Permission denied"}), 403

    content = (request.get_json() or {}).get("content", "").strip()
    if not content:
        return jsonify({"message": "Content is required"}), 400

    ann = Announcement(content=content, posted_by=user_id)
    db.session.add(ann)
    db.session.commit()
    return jsonify({"message": "Announcement posted successfully"}), 201


@announcement_bp.route("", methods=["GET"])
@jwt_required()
def get_announcements():
    announcements = Announcement.query\
        .order_by(Announcement.created_at.desc()).all()

    return jsonify([{
        "id":         a.id,
        "content":    a.content,
        "posted_by":  a.author.name,
        "role":       a.author.role,
        "created_at": a.created_at.strftime("%d %b %Y, %I:%M %p")
    } for a in announcements]), 200
