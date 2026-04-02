import os
from flask import Blueprint, request, jsonify, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models.placement import Placement
from datetime import datetime

placement_bp = Blueprint("placement_bp", __name__, url_prefix="/placement")

# --- FILE CONFIGURATION ---
# Get the absolute path to the backend project root
BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads', 'placements')
ALLOWED_EXTENSIONS = {'pdf'}

# Ensure directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ---------------- ADD PLACEMENT ----------------
@placement_bp.route("/", methods=["POST"])
@jwt_required()
def add_placement():
    user_id = int(get_jwt_identity())
    claims = get_jwt()

    if claims.get("role") != "student":
        return jsonify({"error": "Access denied"}), 403

    # Using request.form for multipart data
    company_name = request.form.get("companyName")
    job_role = request.form.get("jobRole")
    package = request.form.get("package")
    status = request.form.get("status")
    year = request.form.get("placementYear")

    if not company_name or not job_role:
        return jsonify({"error": "Company and Job Role required"}), 400

    # Handle File Upload
    proof_filename = None
    if 'proof_file' in request.files:
        file = request.files['proof_file']
        if file and allowed_file(file.filename):
            original_name = secure_filename(file.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            proof_filename = f"offer_u{user_id}_{timestamp}_{original_name}"
            file.save(os.path.join(UPLOAD_FOLDER, proof_filename))

    new_placement = Placement(
        userId=user_id,
        companyName=company_name,
        jobRole=job_role,
        package=package,
        status=status,
        placementYear=int(year) if year else None,
        proof_path=proof_filename
    )

    db.session.add(new_placement)
    db.session.commit()

    return jsonify({"message": "Placement added successfully"}), 201

# ---------------- GET ALL PLACEMENTS ----------------
@placement_bp.route("/", methods=["GET"])
@jwt_required()
def get_placements():
    user_id = int(get_jwt_identity())
    placements = Placement.query.filter_by(userId=user_id).all()

    result = [{
        "id": p.id,
        "companyName": p.companyName,
        "jobRole": p.jobRole,
        "package": p.package,
        "status": p.status,
        "placementYear": p.placementYear,
        "hasProof": True if p.proof_path else False
    } for p in placements]

    return jsonify(result), 200

# ---------------- SECURE VIEW PROOF ----------------
@placement_bp.route("/view-proof/<int:id>", methods=["GET"])
@jwt_required()
def view_proof(id):
    user_id = int(get_jwt_identity())
    placement = Placement.query.get_or_404(id)

    if placement.userId != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    if not placement.proof_path:
        return jsonify({"error": "No document found"}), 404

    return send_from_directory(UPLOAD_FOLDER, placement.proof_path)

# ---------------- DELETE PLACEMENT ----------------
@placement_bp.route("/<int:id>", methods=["DELETE"])
@jwt_required()
def delete_placement(id):
    user_id = int(get_jwt_identity())
    placement = Placement.query.filter_by(id=id, userId=user_id).first()

    if not placement:
        return jsonify({"error": "Placement not found"}), 404
    
    # Optional: Delete physical file if you want to save space
    if placement.proof_path:
        file_path = os.path.join(UPLOAD_FOLDER, placement.proof_path)
        if os.path.exists(file_path):
            os.remove(file_path)

    db.session.delete(placement)
    db.session.commit()
    return jsonify({"message": "Deleted successfully"}), 200