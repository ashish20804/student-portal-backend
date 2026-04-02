import os
from flask import Blueprint, request, jsonify, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models.activity import Activity
from app.models.studentactivity import StudentActivity
from datetime import datetime

activity_bp = Blueprint("activity", __name__, url_prefix="/activity")

# --- FILE CONFIGURATION ---
BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads', 'certificates')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'

# ---------------- CREATE ACTIVITY ----------------
@activity_bp.route("/", methods=["POST"])
@jwt_required()
def create_activity():
    user_id = int(get_jwt_identity())
    
    # Debugging: Print to see what the backend is getting
    print("Form Data received:", request.form)
    print("Files received:", request.files)

    # Use request.form for text data
    name = request.form.get("activityName")
    category = request.form.get("category")
    level = request.form.get("level", "College")
    achievement = request.form.get("achievement")

    if not name:
        return jsonify({"error": "Activity name is required"}), 400

    # Handle PDF Upload
    final_filename = None
    if 'certificate' in request.files:
        file = request.files['certificate']
        if file and allowed_file(file.filename):
            original = secure_filename(file.filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            final_filename = f"act_u{user_id}_{timestamp}_{original}"
            file.save(os.path.join(UPLOAD_FOLDER, final_filename))

    try:
        # Create Activity using proof_path
        new_activity = Activity(
            activityName=name,
            category=category,
            level=level,
            achievement=achievement,
            proof_path=final_filename 
        )
        db.session.add(new_activity)
        db.session.flush() 

        # Link User
        student_link = StudentActivity(
            userId=user_id,
            activityId=new_activity.activityId
        )
        db.session.add(student_link)
        db.session.commit()

        return jsonify({"message": "Activity and Proof saved successfully"}), 201
    
    except Exception as e:
        db.session.rollback()
        print(f"Database Error: {e}")
        return jsonify({"error": str(e)}), 500

# ---------------- GET MY ACTIVITIES ----------------
@activity_bp.route("/my", methods=["GET"])
@jwt_required()
def my_activities():
    user_id = int(get_jwt_identity())
    joins = StudentActivity.query.filter_by(userId=user_id).all()

    result = []
    for j in joins:
        act = Activity.query.get(j.activityId)
        if act:
            result.append({
                "activityId": act.activityId,
                "activityName": act.activityName,
                "category": act.category,
                "achievement": act.achievement,
                "hasCertificate": True if act.proof_path else False
            })
    return jsonify(result), 200

# ---------------- VIEW CERTIFICATE ----------------
@activity_bp.route("/view-cert/<int:activity_id>", methods=["GET"])
@jwt_required()
def view_certificate(activity_id):
    user_id = int(get_jwt_identity())
    link = StudentActivity.query.filter_by(userId=user_id, activityId=activity_id).first()
    
    if not link:
        return jsonify({"error": "Unauthorized"}), 403

    activity = Activity.query.get(activity_id)
    if not activity or not activity.proof_path:
        return jsonify({"error": "File not found"}), 404

    return send_from_directory(UPLOAD_FOLDER, activity.proof_path)