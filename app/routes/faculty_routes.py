import os
from flask import Blueprint, jsonify, request, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User
from app.models.student import Student
from app.models.faculty import Faculty
from app.models.placement import Placement
from app.models.higherstudies import HigherStudies
from app.models.activity import Activity
from app.models.studentactivity import StudentActivity
from app.models.committeemembership import CommitteeMembership
from app.extensions import db
from sqlalchemy import func

faculty_bp = Blueprint("faculty", __name__, url_prefix="/faculty")

# ==========================================
# HELPER FUNCTIONS
# ==========================================

def faculty_required(user_id):
    """Helper to verify if the user exists in the Faculty table."""
    faculty = Faculty.query.filter_by(userId=user_id).first()
    return faculty is not None

# ==========================================
# 1. FACULTY DASHBOARD
# ==========================================

@faculty_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def faculty_dashboard():
    user_id = int(get_jwt_identity())
    
    user_info = User.query.get(user_id)
    if not user_info or user_info.role != 'faculty':
        return jsonify({"message": "Unauthorized"}), 403

    # Counts for the dashboard stats
    placed_count = Placement.query.filter_by(status="Selected").count()
    higher_studies_count = HigherStudies.query.count()
    extracurricular_count = StudentActivity.query.count()
    activities_count = Activity.query.count()

    return jsonify({
        "userId": user_info.userId,
        "faculty_name": user_info.name,
        "profile_image": user_info.profile_image,
        "placed_students": placed_count,
        "higher_studies_count": higher_studies_count,
        "extracurricular_count": extracurricular_count,
        "total_activities": activities_count,
        "permissions": user_info.get_permissions_list() 
    })

# ==========================================
# 2. STUDENT SEARCH & LISTING
# ==========================================

@faculty_bp.route("/students", methods=["GET"])
@jwt_required()
def get_students():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    if not user or user.role not in ('faculty', 'admin'):
        return jsonify({"message": "Unauthorized"}), 403

    search = request.args.get("search", "").strip()
    semester = request.args.get("semester", "").strip()
    department = request.args.get("department", "").strip()

    query = db.session.query(User, Student).join(
        Student, User.userId == Student.userId
    ).filter(User.role == 'student')

    if search:
        query = query.filter(User.name.ilike(f"%{search}%"))
    if semester:
        query = query.filter(Student.semester == int(semester))
    if department:
        query = query.filter(Student.department == department)

    results = query.all()

    return jsonify([{
        "userId": user.userId,
        "rollNumber": student.rollNumber,
        "name": user.name,
        "email": user.email,
        "department": student.department or "N/A",
        "semester": student.semester or "N/A"
    } for user, student in results]), 200

# ==========================================
# 3. INDIVIDUAL STUDENT DETAILS
# ==========================================

@faculty_bp.route("/student/<int:student_id>", methods=["GET"])
@jwt_required()
def get_student_details(student_id):
    user_id = int(get_jwt_identity())
    faculty_user = User.query.get(user_id)
    
    if not faculty_user or faculty_user.role not in ('faculty', 'admin'):
        return jsonify({"message": "Unauthorized"}), 403

    perms = faculty_user.get_permissions_list()
    user = User.query.get(student_id)
    student = Student.query.filter_by(userId=student_id).first()

    if not user or not student:
        return jsonify({"message": "Student not found"}), 404

    # Placement - only if permitted
    placement_data = None
    if "view_placement" in perms:
        placement = Placement.query.filter_by(userId=student_id).first()
        placement_data = {
            "status": placement.status if placement else "Not Placed",
            "companyName": placement.companyName if placement else None,
            "jobRole": placement.jobRole if placement else None,
            "package": placement.package if placement else None,
            "placementYear": placement.placementYear if placement else None
        }

    # Higher Studies - only if permitted
    higher_studies_data = None
    if "view_higher_studies" in perms:
        higher_studies = HigherStudies.query.filter_by(userId=student_id).all()
        higher_studies_data = [{
            "university": hs.university,
            "course": hs.courseName,
            "country": hs.country,
            "status": hs.admissionStatus
        } for hs in higher_studies]

    # Activities - only if permitted
    activities_data = None
    if "view_activities" in perms:
        activities = db.session.query(Activity).join(
            StudentActivity, Activity.activityId == StudentActivity.activityId
        ).filter(StudentActivity.userId == student_id).all()
        activities_data = [{
            "activityName": act.activityName,
            "category": act.category,
            "level": act.level,
            "achievement": act.achievement
        } for act in activities]

    return jsonify({
        "permissions": perms,
        "basic_info": {
            "name": user.name,
            "email": user.email,
            "rollNumber": student.rollNumber,
            "department": student.department,
            "semester": student.semester,
            "sgpa": student.sgpa,
            "cgpa": student.cgpa,
            "attendance": student.attendance_percentage,
            "phone": user.phoneNumber or "N/A",
            "address": user.address or "N/A"
        },
        "placement": placement_data,
        "higher_studies": higher_studies_data,
        "activities": activities_data
    }), 200

# ==========================================
# 4. BULK DATA RETRIEVAL (OUTER JOIN)
# ==========================================

@faculty_bp.route("/all-higher-studies", methods=["GET"])
@jwt_required()
def get_all_higher_studies():
    user_id = int(get_jwt_identity())
    faculty_user = User.query.get(user_id)

    if not faculty_user or "view_higher_studies" not in faculty_user.get_permissions_list():
        return jsonify({"message": "Access Denied"}), 403

    results = db.session.query(HigherStudies).join(User, User.userId == HigherStudies.userId).filter(User.role == 'student').all()

    data = []
    for hs in results:
        student = Student.query.filter_by(userId=hs.userId).first()
        user = User.query.get(hs.userId)
        data.append({
            "student_name": user.name if user else "N/A",
            "roll_no": student.rollNumber if student else "N/A",
            "university": hs.university or "N/A",
            "courseName": hs.courseName or "N/A",
            "country": hs.country or "N/A",
            "admissionStatus": hs.admissionStatus or "Pending",
            "doc_path": hs.proof_path
        })
    return jsonify(data), 200

@faculty_bp.route("/all-activities", methods=["GET"])
@jwt_required()
def get_all_activities():
    user_id = int(get_jwt_identity())
    faculty_user = User.query.get(user_id)

    if not faculty_user or "view_activities" not in faculty_user.get_permissions_list():
        return jsonify({"message": "Access Denied"}), 403

    results = db.session.query(StudentActivity, Activity).join(Activity, StudentActivity.activityId == Activity.activityId).all()

    data = []
    for sa, act in results:
        user = User.query.get(sa.userId)
        if not user or user.role != 'student':
            continue
        student = Student.query.filter_by(userId=sa.userId).first()
        data.append({
            "student_name": user.name,
            "roll_no": student.rollNumber if student else "N/A",
            "activityName": act.activityName or "N/A",
            "category": act.category or "N/A",
            "level": act.level or "N/A",
            "achievement": act.achievement or "N/A",
            "doc_path": act.proof_path
        })
    return jsonify(data), 200

@faculty_bp.route("/all-placements", methods=["GET"])
@jwt_required()
def get_all_placements():
    user_id = int(get_jwt_identity())
    faculty_user = User.query.get(user_id)

    if not faculty_user or "view_placement" not in faculty_user.get_permissions_list():
        return jsonify({"message": "Access Denied"}), 403

    results = Placement.query.all()

    data = []
    for p in results:
        user = User.query.get(p.userId)
        if not user or user.role != 'student':
            continue
        student = Student.query.filter_by(userId=p.userId).first()
        data.append({
            "student_name": user.name,
            "roll_no": student.rollNumber if student else "N/A",
            "companyName": p.companyName or "N/A",
            "jobRole": p.jobRole or "N/A",
            "package": p.package or "N/A",
            "status": p.status or "N/A",
            "doc_path": p.proof_path
        })
    return jsonify(data), 200
# ==========================================
# 5. FILE SERVING (SUBFOLDER AWARE)
# ==========================================

@faculty_bp.route('/view-proof/<filename>')
@jwt_required()
def view_student_proof(filename):
    """Searches for proof files in specified subfolders and serves them."""
    # Ensure filename is secure and not a path traversal attempt
    base_uploads = os.path.join(os.getcwd(), 'uploads')
    subfolders = ['placements', 'higher_studies', 'certificates']
    
    for folder in subfolders:
        file_path = os.path.join(base_uploads, folder, filename)
        if os.path.exists(file_path):
            return send_from_directory(os.path.join(base_uploads, folder), filename)
    
    return jsonify({"message": "File not found"}), 404
