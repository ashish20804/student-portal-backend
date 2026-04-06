import os
import secrets
import threading
from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_mail import Message as MailMessage
from app.extensions import db, mail
from app.models.user import User
from app.models.student import Student
from app.models.faculty import Faculty
from app.models.activity import Activity
from app.models.committee import Committee
from app.models.placement import Placement
from app.utils.role_required import admin_required

admin_bp = Blueprint("admin_bp", __name__, url_prefix="/admin")

# --- EMAIL UTILITY — runs in background thread so it never blocks the worker ---
def send_activation_email(email, name, token):
    from flask import current_app
    app = current_app._get_current_object()
    frontend_url = app.config.get('FRONTEND_URL', 'http://127.0.0.1:8000')
    activation_link = f"{frontend_url}/activate.html?token={token}"

    def _send():
        with app.app_context():
            try:
                msg = MailMessage("Activate Your Student Portal Account", recipients=[email])
                msg.body = (
                    f"Hello {name},\n\n"
                    f"Your account has been created on the Student Portal.\n\n"
                    f"Click the link below to activate your account and set your password:\n"
                    f"{activation_link}\n\n"
                    f"This link expires in 24 hours.\n\n"
                    f"If you did not expect this email, please ignore it."
                )
                mail.send(msg)
                print(f"Activation email sent to {email}")
            except Exception as e:
                print(f"Activation email failed for {email}: {e}")

    threading.Thread(target=_send, daemon=True).start()

# ==========================================
# 1. DASHBOARD & SYSTEM ANALYTICS (UNTOUCHED)
# ==========================================
@admin_bp.route("/dashboard", methods=["GET"])
@jwt_required()
@admin_required
def admin_dashboard():
    try:
        # Real placement count from DB
        placed_count = db.session.query(Placement.userId).distinct().count()

        # Recent placements from DB
        recent = db.session.query(Placement, Student, User)\
            .join(Student, Placement.userId == Student.userId)\
            .join(User, Student.userId == User.userId)\
            .order_by(Placement.id.desc()).limit(5).all()

        recent_placements = [{
            'name':    u.name,
            'company': p.companyName,
            'package': f"{p.package} LPA" if p.package else 'N/A'
        } for p, s, u in recent]

        stats = {
            "total_students":   Student.query.count(),
            "total_faculty":    Faculty.query.count(),
            "total_activities": Activity.query.count(),
            "total_committees": Committee.query.count(),
            "placed_students":  placed_count,
            "recent_placements": recent_placements,
            "notifications": [
                {"id": 1, "text": "System running on latest DB snapshot", "type": "success"},
                {"id": 2, "text": "New placement drive: Amazon India",     "type": "info"}
            ]
        }
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==========================================
# 2. USER MANAGEMENT & RBAC
# ==========================================
@admin_bp.route("/users", methods=["GET"])
@jwt_required()
@admin_required
def get_all_users():
    search = request.args.get("search")
    dept_filter = request.args.get("department")

    query = db.session.query(User)
    if search:
        query = query.filter((User.name.ilike(f"%{search}%")) | (User.email.ilike(f"%{search}%")))
    
    users = query.all()
    result = []
    
    for user in users:
        dept = "N/A"
        if user.role == "student":
            s = Student.query.filter_by(userId=user.userId).first()
            if s: dept = s.department
        elif user.role == "faculty":
            f = Faculty.query.filter_by(userId=user.userId).first()
            if f: dept = f.department
        
        if dept_filter and dept != dept_filter:
            continue

        result.append({
            "userId": user.userId,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "department": dept,
            "permissions": user.get_permissions_list()
        })
    return jsonify(result), 200

# --- UNIFIED ADD USER ROUTE FOR FRONTEND ---
@admin_bp.route("/users/add", methods=["POST"])
@jwt_required()
@admin_required
def add_user_unified():
    data = request.get_json()
    email = data.get("email")
    role = data.get("role")
    name = data.get("name")

    if not email or not name or not role:
        return jsonify({"message": "Name, email, and role are required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already exists"}), 400

    try:
        activation_token = secrets.token_urlsafe(32)

        new_user = User(
            name=name,
            email=email,
            role=role,
            phoneNumber=data.get("phoneNumber"),
            address=data.get("address"),
            is_active=False,
            activation_token=activation_token
        )
        new_user.set_password(secrets.token_hex(16))  # random unusable password until activated
        db.session.add(new_user)
        db.session.flush()

        if role == "student":
            roll_no = data.get("roll_no") or data.get("rollNumber")
            if not roll_no:
                db.session.rollback()
                return jsonify({"message": "Roll number is required for students"}), 400
            db.session.add(Student(
                userId=new_user.userId,
                rollNumber=roll_no,
                department=data.get("department"),
                program=data.get("program", "B.Tech"),
                semester=int(data.get("semester", 1)),
                sgpa=float(data.get("sgpa", 0.0)),
                cgpa=float(data.get("cgpa", 0.0)),
                attendance_percentage=float(data.get("attendance", 0.0))
            ))
        elif role == "faculty":
            db.session.add(Faculty(
                userId=new_user.userId,
                department=data.get("department")
            ))

        db.session.commit()

        # Send email in background — never blocks the response
        send_activation_email(email, name, activation_token)
        return jsonify({"message": f"{role.capitalize()} added successfully. Activation email will be sent shortly."}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@admin_bp.route("/users/<int:user_id>/update-access", methods=["PUT"])
@jwt_required()
@admin_required
def update_user_access(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    if "role" in data:
        user.role = data["role"]
    if "permissions" in data:
        perms_list = data.get("permissions", [])
        user.permissions = ",".join(perms_list)
    try:
        db.session.commit()
        return jsonify({"message": "Access levels successfully updated!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# ==========================================
# 3. ANNOUNCEMENTS
# ==========================================
@admin_bp.route("/announce", methods=["POST"])
@jwt_required()
@admin_required
def post_announcement():
    from app.models.announcement import Announcement
    user_id = int(get_jwt_identity())
    data = request.get_json()
    content = (data or {}).get("content", "").strip()
    if not content:
        return jsonify({"message": "Announcement content is empty"}), 400
    ann = Announcement(content=content, posted_by=user_id)
    db.session.add(ann)
    db.session.commit()
    return jsonify({"message": "Announcement broadcasted successfully"}), 201

# ==========================================
# 4. USER DELETION & RESET
# ==========================================
from app.models.higherstudies import HigherStudies
from app.models.placement import Placement
from app.models.studentactivity import StudentActivity
from app.models.committeemembership import CommitteeMembership
from app.models.testimonial import Testimonial
from app.models.message import Message

@admin_bp.route("/users/<int:user_id>", methods=["DELETE"])
@jwt_required()
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    try:
        # Delete all dependent records in correct order
        Message.query.filter(
            (Message.senderId == user_id) | (Message.receiverId == user_id)
        ).delete(synchronize_session=False)
        Testimonial.query.filter_by(userId=user_id).delete()
        CommitteeMembership.query.filter_by(userId=user_id).delete()
        StudentActivity.query.filter_by(userId=user_id).delete()
        Placement.query.filter_by(userId=user_id).delete()
        HigherStudies.query.filter_by(userId=user_id).delete()
        Student.query.filter_by(userId=user_id).delete()
        Faculty.query.filter_by(userId=user_id).delete()
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "User and all associated records removed"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@admin_bp.route("/users/<int:user_id>/reset-password", methods=["PUT"])
@jwt_required()
@admin_required
def reset_password(user_id):
    user = User.query.get_or_404(user_id)
    data = request.get_json()
    if not data.get("password"):
        return jsonify({"message": "Password is required"}), 400
    user.set_password(data.get("password"))
    db.session.commit()
    return jsonify({"message": "Password updated successfully"}), 200

# ==========================================
# 5. STUDENT ACADEMIC DETAILS MANAGEMENT
# ==========================================
@admin_bp.route("/students/<int:user_id>/academic", methods=["GET"])
@jwt_required()
@admin_required
def get_student_academic(user_id):
    student = Student.query.filter_by(userId=user_id).first()
    if not student:
        return jsonify({"error": "Student not found"}), 404
    
    return jsonify({
        "rollNumber": student.rollNumber,
        "program": student.program,
        "semester": student.semester,
        "department": student.department,
        "sgpa": student.sgpa,
        "cgpa": student.cgpa,
        "attendance_percentage": student.attendance_percentage
    }), 200

@admin_bp.route("/students/<int:user_id>/academic", methods=["PUT"])
@jwt_required()
@admin_required
def update_student_academic(user_id):
    student = Student.query.filter_by(userId=user_id).first()
    if not student:
        return jsonify({"error": "Student not found"}), 404
    
    data = request.get_json()
    
    try:
        if "rollNumber" in data:
            student.rollNumber = data["rollNumber"]
        if "program" in data:
            student.program = data["program"]
        if "semester" in data:
            student.semester = int(data["semester"])
        if "department" in data:
            student.department = data["department"]
        if "sgpa" in data:
            student.sgpa = float(data["sgpa"])
        if "cgpa" in data:
            student.cgpa = float(data["cgpa"])
        if "attendance_percentage" in data:
            student.attendance_percentage = float(data["attendance_percentage"])
        
        db.session.commit()
        print(f"✅ Academic details updated for student: {user_id}")
        return jsonify({"message": "Academic details updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error updating academic details: {str(e)}")
        return jsonify({"error": str(e)}), 500