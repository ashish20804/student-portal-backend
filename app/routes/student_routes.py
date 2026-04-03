import os
from flask import Blueprint, jsonify, request, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from werkzeug.utils import secure_filename
from app.models.user import User
from app.models.student import Student
from app.models.faculty import Faculty # Added this import
from app.extensions import db

# Cleaner structure
student_bp = Blueprint("student_bp", __name__, url_prefix="/student")

# Portable profile photo path — works on both Windows (local) and Linux (Render)
BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
PROFILE_UPLOAD_PATH = os.path.join(BASE_DIR, 'uploads', 'profiles')
os.makedirs(PROFILE_UPLOAD_PATH, exist_ok=True)

def extract_roll_number(email):
    """Helper to extract '22BCE024' from '22bce024@nirmauni.ac.in'"""
    if not email:
        return None
    return email.split('@')[0].upper()

def normalize_profile_image(profile_image):
    """Returns None for old filename-based images (they no longer exist on server).
    Returns the value as-is if it's already a base64 data URL."""
    if not profile_image:
        return None
    if profile_image.startswith('data:'):
        return profile_image  # already base64 data URL
    return None  # old filename — file doesn't exist on Render, return None so avatar initial shows

# ---------------- PHOTO DISPLAY ROUTE ----------------
@student_bp.route('/display-photo/<path:filename>', methods=["GET"])
def display_photo(filename):
    """Legacy route — kept for backward compatibility with old filename-based photos"""
    return send_from_directory(PROFILE_UPLOAD_PATH, filename)

# ---------------- STUDENT/FACULTY DASHBOARD ----------------
@student_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def student_dashboard():
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    role = claims.get("role")

    # Allowed faculty and students to access base dashboard data
    if role not in ["student", "faculty"]:
        return jsonify({"error": "Access denied"}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Base response
    response_data = {
        "name": user.name,
        "email": user.email,
        "profile_image": normalize_profile_image(user.profile_image)
    }

    if role == "student":
        student = Student.query.get(user_id)
        if student:
            response_data.update({
                "rollNumber": student.rollNumber or extract_roll_number(user.email),
                "program": student.program,
                "semester": student.semester,
                "department": student.department,
                "sgpa": student.sgpa,
                "cgpa": student.cgpa,
                "attendance_percentage": student.attendance_percentage
            })
    elif role == "faculty":
        faculty = Faculty.query.get(user_id)
        if faculty:
            response_data.update({
                "rollNumber": faculty.designation, # Using rollNumber key for JS compatibility
                "department": faculty.department
            })

    return jsonify(response_data), 200


# ---------------- GET PROFILE (MODIFIED FOR BOTH ROLES) ----------------
@student_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    role = claims.get("role")

    # Removed the 'if role != student' block to allow Faculty
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Profile not found"}), 404

    # Base data
    profile_info = {
        "userId": user.userId,
        "name": user.name,
        "email": user.email,
        "phoneNumber": user.phoneNumber,
        "address": user.address,
        "profile_image": normalize_profile_image(user.profile_image),
        "role": role
    }

    if role == "student":
        student = Student.query.get(user_id)
        if student:
            profile_info.update({
                "rollNumber": student.rollNumber or extract_roll_number(user.email),
                "program": student.program,
                "semester": student.semester,
                "department": student.department,
                "sgpa": student.sgpa,
                "cgpa": student.cgpa,
                "attendance_percentage": student.attendance_percentage
            })
    elif role == "faculty":
        faculty = Faculty.query.get(user_id)
        if faculty:
            profile_info.update({
                "rollNumber": faculty.designation, # Sent as rollNumber so JS doesn't show 'Loading...'
                "department": faculty.department
            })

    return jsonify(profile_info), 200


# ---------------- UPDATE PROFILE ----------------
@student_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    role = claims.get("role")

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Profile not found"}), 404

    try:
        # 1. Handle Profile Image Upload — store as base64 in DB (works on Render + local)
        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file and file.filename != '':
                import base64
                ext = file.filename.rsplit('.', 1)[-1].lower()
                mime = 'image/jpeg' if ext in ('jpg', 'jpeg') else f'image/{ext}'
                encoded = base64.b64encode(file.read()).decode('utf-8')
                user.profile_image = f"data:{mime};base64,{encoded}"

        # 2. Update User Table Fields
        user.name = request.form.get("name", user.name)
        user.phoneNumber = request.form.get("phoneNumber", user.phoneNumber)
        user.address = request.form.get("address", user.address)

        # 3. Role-specific updates
        if role == "student":
            student = Student.query.get(user_id)
            if student:
                student.program = request.form.get("program", student.program)
                student.department = request.form.get("department", student.department)
                if "semester" in request.form:
                    student.semester = int(request.form.get("semester"))
                student.rollNumber = extract_roll_number(user.email)
                
        # Optional: Faculty can also update their department if allowed
        elif role == "faculty":
            faculty = Faculty.query.get(user_id)
            if faculty:
                faculty.department  = request.form.get("department",  faculty.department)
                faculty.designation = request.form.get("designation", faculty.designation)

        db.session.commit()

        # Build response to ensure rollNumber (or Designation) is returned
        return_data = {
            "message": "Profile updated successfully",
            "name": user.name,
            "profile_image": user.profile_image
        }
        
        if role == "student":
            student = Student.query.get(user_id)
            return_data["rollNumber"] = student.rollNumber if student else ""
        else:
            faculty = Faculty.query.get(user_id)
            return_data["rollNumber"] = faculty.designation if faculty else "Faculty"

        return jsonify(return_data), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Update failed: {str(e)}"}), 500