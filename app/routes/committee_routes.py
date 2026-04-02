from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.committee import Committee
from app.models.committeemembership import CommitteeMembership
from app.models.user import User
from datetime import date

committee_bp = Blueprint("committee", __name__, url_prefix="/committee")

@committee_bp.route("/", methods=["POST"])
@jwt_required()
def create_committee():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    try:
        # 1. Create the Committee record
        new_committee = Committee(
            committeeName=data.get("committeeName"),
            type=data.get("type")
        )
        db.session.add(new_committee)
        db.session.flush()

        # 2. Automatically make the creator a member
        membership = CommitteeMembership(
            userId=user_id,
            committeeCode=new_committee.committeeCode,
            role="Member",
            joinDate=date.today()
        )
        db.session.add(membership)
        
        db.session.commit()
        return jsonify({"message": "Committee created and joined successfully"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@committee_bp.route("/", methods=["GET"])
def get_committees():
    committees = Committee.query.all()
    result = []
    for c in committees:
        result.append({
            "committeeCode": c.committeeCode,
            "committeeName": c.committeeName,
            "type": c.type
        })
    return jsonify(result), 200

@committee_bp.route("/join/<int:code>", methods=["POST"])
@jwt_required()
def join_committee(code):
    user_id = int(get_jwt_identity())

    existing = CommitteeMembership.query.filter_by(
        userId=user_id,
        committeeCode=code
    ).first()

    if existing:
        return jsonify({"message": "Already member"}), 400

    membership = CommitteeMembership(
        userId=user_id,
        committeeCode=code
    )

    db.session.add(membership)
    db.session.commit()
    return jsonify({"message": "Joined committee"}), 201

@committee_bp.route("/my", methods=["GET"])
@jwt_required()
def my_committees():
    user_id = int(get_jwt_identity())
    memberships = CommitteeMembership.query.filter_by(userId=user_id).all()

    result = []
    for m in memberships:
        committee = Committee.query.get(m.committeeCode)
        if committee:
            result.append({
                "committeeCode": committee.committeeCode,
                "committeeName": committee.committeeName,
                "type": committee.type,
                "role": m.role,
                "joinDate": m.joinDate.isoformat() if m.joinDate else None
            })
    return jsonify(result), 200

@committee_bp.route("/members/<int:code>", methods=["GET"])
@jwt_required()
def get_committee_members(code):
    members = CommitteeMembership.query.filter_by(committeeCode=code).all()
    result = []
    for m in members:
        user = User.query.get(m.userId)
        if user:
            result.append({
                "userId": user.userId,
                "name": user.name,
                "email": user.email,
                "role": m.role
            })
    return jsonify(result), 200