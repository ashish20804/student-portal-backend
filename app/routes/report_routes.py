from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from sqlalchemy import func
from app.extensions import db

# Models
from app.models.user import User
from app.models.student import Student
from app.models.placement import Placement 
from app.models.higherstudies import HigherStudies 
from app.models.activity import Activity
from app.models.studentactivity import StudentActivity # Ensure both are imported

# Utils
from app.utils.role_required import admin_required

report_bp = Blueprint('report_bp', __name__, url_prefix='/admin/reports')

# --- 1. PLACEMENT ROUTES ---

@report_bp.route("/placement-stats", methods=["GET"])
@jwt_required()
@admin_required
def placement_stats():
    year = request.args.get("year")
    
    total_students = Student.query.count()
    
    # Filter placements by year if provided
    placement_query = db.session.query(Student)\
        .join(Placement, Student.userId == Placement.userId)
    
    if year:
        placement_query = placement_query.filter(Placement.placementYear == year)
    
    placed_students = placement_query.count()

    # Department-wise distribution for pie chart (filtered by year)
    dept_query = db.session.query(
        Student.department,
        func.count(Placement.id)
    ).join(Placement, Student.userId == Placement.userId)
    
    if year:
        dept_query = dept_query.filter(Placement.placementYear == year)
    
    department_stats = dept_query.group_by(Student.department).all()

    return jsonify({
        "total_students": total_students,
        "placed_students": placed_students,
        "distLabels": [dept if dept else "General" for dept, count in department_stats],
        "distData": [count for dept, count in department_stats]
    }), 200

@report_bp.route("/placement/year-wise", methods=["GET"])
@jwt_required()
@admin_required
def year_wise_placement():
    data = db.session.query(
        Placement.placementYear,
        func.count(Placement.id)
    ).group_by(Placement.placementYear)\
     .order_by(Placement.placementYear).all()

    return jsonify({
        "labels": [str(year) for year, count in data],
        "counts": [count for year, count in data]
    }), 200

@report_bp.route("/placement", methods=["GET"])
@jwt_required()
@admin_required
def placement_list():
    from datetime import datetime
    dept = request.args.get("department")
    year = request.args.get("year")
    roll_from = request.args.get("roll_from")
    roll_to = request.args.get("roll_to")
    month_from = request.args.get("month_from")  # format: YYYY-MM
    month_to = request.args.get("month_to")      # format: YYYY-MM
    status = request.args.get("status")          # "placed" or "unplaced"

    if status == "unplaced":
        placed_user_ids = db.session.query(Placement.userId).subquery()
        query = db.session.query(Student).join(User, Student.userId == User.userId).filter(
            User.role == 'student',
            Student.userId.notin_(placed_user_ids)
        )
        if dept and dept != "All Department":
            query = query.filter(Student.department == dept)
        if roll_from:
            query = query.filter(Student.rollNumber >= roll_from)
        if roll_to:
            query = query.filter(Student.rollNumber <= roll_to)
        results = query.all()
        return jsonify([{
            "roll_no": s.rollNumber,
            "name": s.user.name,
            "dept": s.department,
            "company": "Not Placed",
            "package": "-",
            "year": "-"
        } for s in results]), 200

    # placed or all — both use the placement join
    query = db.session.query(Placement, Student).join(Student, Placement.userId == Student.userId)

    if dept and dept != "All Department":
        query = query.filter(Student.department == dept)
    if year:
        query = query.filter(Placement.placementYear == year)
    if roll_from:
        query = query.filter(Student.rollNumber >= roll_from)
    if roll_to:
        query = query.filter(Student.rollNumber <= roll_to)
    if month_from:
        try:
            dt_from = datetime.strptime(month_from, "%Y-%m")
            query = query.filter(Placement.created_at >= dt_from)
        except ValueError:
            pass
    if month_to:
        try:
            dt_to = datetime.strptime(month_to, "%Y-%m")
            # Include the entire month_to month
            if dt_to.month == 12:
                dt_to = dt_to.replace(year=dt_to.year + 1, month=1)
            else:
                dt_to = dt_to.replace(month=dt_to.month + 1)
            query = query.filter(Placement.created_at < dt_to)
        except ValueError:
            pass

    results = query.all()
    return jsonify([{
        "roll_no": s.rollNumber,
        "name": s.user.name,
        "dept": s.department,
        "company": p.companyName,
        "package": p.package,
        "year": p.placementYear
    } for p, s in results]), 200

# --- 2. HIGHER STUDIES ROUTES ---

@report_bp.route("/higher-studies/year-wise", methods=["GET"])
@jwt_required()
@admin_required
def year_wise_higher_studies():
    data = db.session.query(
        func.extract('year', HigherStudies.applicationDate),
        func.count(HigherStudies.id)
    ).filter(HigherStudies.applicationDate.isnot(None))\
     .group_by(func.extract('year', HigherStudies.applicationDate))\
     .order_by(func.extract('year', HigherStudies.applicationDate)).all()

    return jsonify({
        "labels": [str(int(year)) for year, count in data if year],
        "counts": [count for year, count in data if year]
    }), 200

@report_bp.route("/higher-studies-stats", methods=["GET"])
@jwt_required()
@admin_required
def higher_studies_stats():
    year = request.args.get("year")
    
    # Department-wise distribution for pie chart
    dept_query = db.session.query(
        Student.department,
        func.count(HigherStudies.id)
    ).join(Student, HigherStudies.userId == Student.userId)\
     .join(User, Student.userId == User.userId)\
     .filter(User.role == 'student')
    
    if year:
        dept_query = dept_query.filter(func.extract('year', HigherStudies.applicationDate) == year)
    
    department_stats = dept_query.group_by(Student.department).all()

    return jsonify({
        "distLabels": [dept if dept else "General" for dept, count in department_stats],
        "distData": [count for dept, count in department_stats]
    }), 200

@report_bp.route("/higher-studies", methods=["GET"])
@jwt_required()
@admin_required
def higher_studies_list():
    from datetime import datetime, date
    dept = request.args.get("department")
    year = request.args.get("year")
    roll_from = request.args.get("roll_from")
    roll_to = request.args.get("roll_to")
    month_from = request.args.get("month_from")  # format: YYYY-MM
    month_to = request.args.get("month_to")      # format: YYYY-MM
    status = request.args.get("status")          # "higher_studies" or "no_higher_studies"

    if status == "no_higher_studies":
        hs_user_ids = db.session.query(HigherStudies.userId).subquery()
        query = db.session.query(Student).join(User, Student.userId == User.userId).filter(
            User.role == 'student',
            (Student.isPlanningHigherStudies == False) | (Student.userId.notin_(hs_user_ids))
        )
        if dept and dept != "All Department":
            query = query.filter(Student.department == dept)
        if roll_from:
            query = query.filter(Student.rollNumber >= roll_from)
        if roll_to:
            query = query.filter(Student.rollNumber <= roll_to)
        results = query.all()
        return jsonify([{
            "roll_no": s.rollNumber,
            "name": s.user.name,
            "dept": s.department,
            "university": "Not Applicable",
            "course": "-",
            "year": "-"
        } for s in results]), 200

    # higher_studies or all — join HigherStudies table
    if status == "all":
        query = db.session.query(HigherStudies, Student)\
            .outerjoin(Student, HigherStudies.userId == Student.userId)\
            .join(User, Student.userId == User.userId)\
            .filter(User.role == 'student')
    else:
        # higher_studies: only students WITH a HigherStudies record
        query = db.session.query(HigherStudies, Student)\
            .join(Student, HigherStudies.userId == Student.userId)\
            .join(User, Student.userId == User.userId)\
            .filter(User.role == 'student')

    if dept and dept != "All Department":
        query = query.filter(Student.department == dept)
    if year:
        query = query.filter(func.extract('year', HigherStudies.applicationDate) == year)
    if roll_from:
        query = query.filter(Student.rollNumber >= roll_from)
    if roll_to:
        query = query.filter(Student.rollNumber <= roll_to)
    if month_from:
        try:
            d_from = datetime.strptime(month_from, "%Y-%m").date()
            query = query.filter(HigherStudies.applicationDate >= d_from)
        except ValueError:
            pass
    if month_to:
        try:
            d_to = datetime.strptime(month_to, "%Y-%m").date()
            if d_to.month == 12:
                d_to = d_to.replace(year=d_to.year + 1, month=1)
            else:
                d_to = d_to.replace(month=d_to.month + 1)
            query = query.filter(HigherStudies.applicationDate < d_to)
        except ValueError:
            pass

    results = query.all()
    return jsonify([{
        "roll_no": s.rollNumber,
        "name": s.user.name,
        "dept": s.department,
        "university": h.university,
        "course": h.courseName,
        "year": str(int(h.applicationDate.year)) if h.applicationDate else "N/A"
    } for h, s in results]), 200

# --- 3. ACTIVITY ROUTES ---

@report_bp.route("/activity", methods=["GET"])
@jwt_required()
@admin_required
def activity_report_table():
    dept = request.args.get("department")
    year = request.args.get("year")
    
    # Order of results in query is (Activity, Student)
    query = db.session.query(Activity, Student)\
        .join(StudentActivity, Activity.activityId == StudentActivity.activityId)\
        .join(Student, StudentActivity.userId == Student.userId)

    if dept and dept != "All Department":
        query = query.filter(Student.department == dept)

    results = query.all()
    
    return jsonify([{
        "roll_no": s.rollNumber,
        "name": s.user.name, 
        "dept": s.department,
        "activity_name": a.activityName,
        "category": a.category,
        "achievement": a.achievement,
        "year": year if year else "N/A"
    } for a, s in results]), 200

@report_bp.route("/activity/year-wise", methods=["GET"])
@jwt_required()
@admin_required
def year_wise_activity():
    # Group by category for bar chart (since no date field exists)
    data = db.session.query(
        Activity.category,
        func.count(Activity.activityId)
    ).group_by(Activity.category).all()
    
    return jsonify({
        "labels": [cat if cat else "Other" for cat, count in data],
        "counts": [count for cat, count in data]
    }), 200

@report_bp.route("/activity-stats", methods=["GET"])
@jwt_required()
@admin_required
def activity_stats():
    year = request.args.get("year")
    
    # Department-wise distribution for pie chart
    dept_query = db.session.query(
        Student.department,
        func.count(Activity.activityId)
    ).join(StudentActivity, Activity.activityId == StudentActivity.activityId)\
     .join(Student, StudentActivity.userId == Student.userId)
    
    department_stats = dept_query.group_by(Student.department).all()

    return jsonify({
        "distLabels": [dept if dept else "General" for dept, count in department_stats],
        "distData": [count for dept, count in department_stats]
    }), 200
