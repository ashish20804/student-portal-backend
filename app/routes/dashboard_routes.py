from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt

dashboard_bp = Blueprint("dashboard_bp", __name__, url_prefix="/dashboard")

@dashboard_bp.route("/", methods=["GET"])
@jwt_required()
def dashboard():
    claims = get_jwt()
    role = claims.get("role")

    if role == "admin":
        return jsonify({"message": "Welcome to Admin Dashboard"})
    elif role == "student":
        return jsonify({"message": "Welcome to Student Dashboard"})
    else:
        return jsonify({"message": "Welcome to Dashboard"})
