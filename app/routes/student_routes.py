import os
import io
import base64
from flask import Blueprint, jsonify, request, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.models.user import User
from app.models.student import Student
from app.models.faculty import Faculty
from app.extensions import db

student_bp = Blueprint("student_bp", __name__, url_prefix="/student")

# Keep upload path for legacy display-photo route
BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
PROFILE_UPLOAD_PATH = os.path.join(BASE_DIR, 'uploads', 'profiles')
os.makedirs(PROFILE_UPLOAD_PATH, exist_ok=True)


def extract_roll_number(email):
    if not email:
        return None
    return email.split('@')[0].upper()


def bytes_to_data_url(image_bytes):
    """Convert raw image bytes stored in DB to a base64 data URL for the frontend."""
    if not image_bytes:
        return None
    try:
        encoded = base64.b64encode(image_bytes).decode('utf-8')
        return f"data:image/jpeg;base64,{encoded}"
    except Exception:
        return None


def resize_image(file_bytes, max_size=300):
    """
    Resize image to max_size x max_size px and convert to JPEG.
    Uses Pillow if available, otherwise returns compressed bytes as-is.
    Max 300px keeps the file under ~30KB which fits easily in MEDIUMBLOB.
    """
    try:
        from PIL import Image
        img = Image.open(io.BytesIO(file_bytes))
        img = img.convert('RGB')  # ensure JPEG-compatible
        img.thumbnail((max_size, max_size), Image.LANCZOS)
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=75, optimize=True)
        return output.getvalue()
    except ImportError:
        # Pillow not installed — store raw bytes (still works, just larger)
        return file_bytes
    except Exception:
        return file_bytes


# ---------------- PHOTO DISPLAY ROUTE (legacy) ----------------
@student_bp.route('/display-photo/<path:filename>', methods=["GET"])
def display_photo(filename):
    return send_from_directory(PROFILE_UPLOAD_PATH, filename)


# ---------------- STUDENT/FACULTY DASHBOARD ----------------
@student_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def student_dashboard():
    user_id = int(get_jwt_identity())
    claims  = get_jwt()
    role    = claims.get("role")

    if role not in ["student", "faculty"]:
        return jsonify({"error": "Access denied"}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    response_data = {
        "name":          user.name,
        "email":         user.email,
        "profile_image": bytes_to_data_url(user.profile_image)
    }

    if role == "student":
        student = Student.query.get(user_id)
        if student:
            response_data.update({
                "userId":                user.userId,
                "rollNumber":            student.rollNumber or extract_roll_number(user.email),
                "program":               student.program,
                "semester":              student.semester,
                "department":            student.department,
                "sgpa":                  student.sgpa,
                "cgpa":                  student.cgpa,
                "attendance_percentage": student.attendance_percentage
            })
    elif role == "faculty":
        faculty = Faculty.query.get(user_id)
        if faculty:
            response_data.update({
                "userId":     user.userId,
                "rollNumber": faculty.designation,
                "department": faculty.department
            })

    return jsonify(response_data), 200


# ---------------- GET PROFILE ----------------
@student_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    user_id = int(get_jwt_identity())
    claims  = get_jwt()
    role    = claims.get("role")

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Profile not found"}), 404

    profile_info = {
        "userId":        user.userId,
        "name":          user.name,
        "email":         user.email,
        "phoneNumber":   user.phoneNumber,
        "address":       user.address,
        "profile_image": bytes_to_data_url(user.profile_image),
        "role":          role
    }

    if role == "student":
        student = Student.query.get(user_id)
        if student:
            profile_info.update({
                "rollNumber": student.rollNumber or extract_roll_number(user.email),
                "program":    student.program,
                "semester":   student.semester,
                "department": student.department,
                "sgpa":       student.sgpa,
                "cgpa":       student.cgpa,
                "attendance_percentage": student.attendance_percentage
            })
    elif role == "faculty":
        faculty = Faculty.query.get(user_id)
        if faculty:
            profile_info.update({
                "rollNumber": faculty.designation,
                "department": faculty.department
            })

    return jsonify(profile_info), 200


# ---------------- UPDATE PROFILE ----------------
@student_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    user_id = int(get_jwt_identity())
    claims  = get_jwt()
    role    = claims.get("role")

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Profile not found"}), 404

    try:
        # 1. Handle Profile Image — resize and store as bytes in MEDIUMBLOB
        if 'profile_image' in request.files:
            file = request.files['profile_image']
            if file and file.filename != '':
                raw_bytes = file.read()
                user.profile_image = resize_image(raw_bytes)  # stored as bytes

        # 2. Update User fields
        user.name        = request.form.get("name",        user.name)
        user.phoneNumber = request.form.get("phoneNumber", user.phoneNumber)
        user.address     = request.form.get("address",     user.address)

        # 3. Role-specific updates
        if role == "student":
            student = Student.query.get(user_id)
            if student:
                student.program    = request.form.get("program",    student.program)
                student.department = request.form.get("department", student.department)
                if "semester" in request.form:
                    student.semester = int(request.form.get("semester"))
                student.rollNumber = extract_roll_number(user.email)
        elif role == "faculty":
            faculty = Faculty.query.get(user_id)
            if faculty:
                faculty.department  = request.form.get("department",  faculty.department)
                faculty.designation = request.form.get("designation", faculty.designation)

        db.session.commit()

        return_data = {
            "message":       "Profile updated successfully",
            "name":          user.name,
            "profile_image": bytes_to_data_url(user.profile_image)
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
