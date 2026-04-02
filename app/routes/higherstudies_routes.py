import os
from flask import Blueprint, request, jsonify, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models.higherstudies import HigherStudies
from app.models.student import Student
from datetime import datetime

higherstudies_bp = Blueprint("higherstudies", __name__, url_prefix="/higherstudies")

# Configure where to save
UPLOAD_FOLDER = os.path.join('uploads', 'higher_studies')
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@higherstudies_bp.route("/toggle-planning", methods=["POST"])
@jwt_required()
def toggle_planning():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    status = data.get("status")
    student = Student.query.filter_by(userId=user_id).first()
    
    if not student:
        return jsonify({"error": "Student profile not found"}), 404

    student.isPlanningHigherStudies = status
    db.session.commit()
    return jsonify({"message": "Planning status updated", "isPlanning": student.isPlanningHigherStudies}), 200

@higherstudies_bp.route("/", methods=["POST"])
@jwt_required()
def add_application():
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    
    if claims.get("role") != "student":
        return jsonify({"error": "Access denied"}), 403

    # Important: We use request.form because we are sending Multipart data
    university = request.form.get("university")
    country = request.form.get("country")
    courseName = request.form.get("courseName")
    admissionStatus = request.form.get("admissionStatus")
    app_date_str = request.form.get("applicationDate")

    student = Student.query.get(user_id)
    if not student or not student.isPlanningHigherStudies:
        return jsonify({"error": "Please select 'Yes' for Higher Studies planning first"}), 400

    # Handle File Upload
    proof_filename = None
    if 'proof_file' in request.files:
        file = request.files['proof_file']
        if file and allowed_file(file.filename):
            # Create a unique filename: user14_timestamp_filename.pdf
            original_name = secure_filename(file.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            proof_filename = f"user{user_id}_{timestamp}_{original_name}"
            file.save(os.path.join(UPLOAD_FOLDER, proof_filename))

    new_app = HigherStudies(
        userId=user_id,
        university=university,
        country=country,
        courseName=courseName,
        admissionStatus=admissionStatus,
        applicationDate=datetime.strptime(app_date_str, "%Y-%m-%d") if app_date_str else None,
        proof_path=proof_filename # Save only the name, not the full computer path
    )

    db.session.add(new_app)
    db.session.commit()
    return jsonify({"message": "Application saved successfully"}), 201

@higherstudies_bp.route("/", methods=["GET"])
@jwt_required()
def get_applications():
    user_id = int(get_jwt_identity())
    student = Student.query.get(user_id)
    apps = HigherStudies.query.filter_by(userId=user_id).all()

    result = [{
        "id": a.id,
        "university": a.university,
        "country": a.country,
        "courseName": a.courseName,
        "admissionStatus": a.admissionStatus,
        "applicationDate": a.applicationDate.strftime("%Y-%m-%d") if a.applicationDate else None,
        "hasProof": True if a.proof_path else False
    } for a in apps]

    return jsonify({"applications": result, "isPlanning": student.isPlanningHigherStudies if student else False}), 200

# Securely view the PDF
@higherstudies_bp.route("/view-proof/<int:app_id>", methods=["GET"])
@jwt_required()
def view_proof(app_id):
    user_id = int(get_jwt_identity())
    application = HigherStudies.query.get_or_404(app_id)

    # Security Check: Only the owner can see their proof
    if application.userId != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    if not application.proof_path:
        return jsonify({"error": "No document uploaded for this application"}), 404

    return send_from_directory(os.path.abspath(UPLOAD_FOLDER), application.proof_path)