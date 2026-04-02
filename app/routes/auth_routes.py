import random
import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    set_access_cookies,
    unset_jwt_cookies,
    get_jwt,
    verify_jwt_in_request
)
from flask_mail import Message
from app.models.user import User
from app.models.student import Student
from app.extensions import db, mail  # Ensure mail is imported from extensions

auth_bp = Blueprint("auth_bp", __name__)

def extract_roll(email):
    """Extracts '22BCE024' from '22bce024@nirmauni.ac.in'"""
    if not email or '@' not in email:
        return "UNKNOWN"
    return email.split('@')[0].upper()

# =========================
# DEBUG: AUTH CHECK ROUTE
# =========================
@auth_bp.route("/auth-check", methods=["GET"])
def auth_check():
    try:
        verify_jwt_in_request()
        claims = get_jwt()
        return jsonify({
            "status": "Logged In",
            "role_in_token": claims.get("role"),
            "user_id": claims.get("sub"),
            "full_claims": claims
        }), 200
    except Exception as e:
        return jsonify({
            "status": "Not Logged In",
            "error": str(e)
        }), 401

# =========================
# USER REGISTRATION
# =========================
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    name = data.get("name", "New Student")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 400

    try:
        # 1. Create User Entry
        new_user = User(name=name, email=email, role="student")
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.flush() 

        # 2. Create Student Profile linked to User
        new_student = Student(
            userId=new_user.userId,
            rollNumber=extract_roll(email),
            isPlanningHigherStudies=False
        )
        
        db.session.add(new_student)
        db.session.commit()

        # 3. SEND WELCOME EMAIL
        try:
            msg = Message("Welcome to Nirma Student Portal", recipients=[email])
            msg.body = f"Hello {name},\n\nYour registration is successful!\n\nCredentials:\nEmail: {email}\nPassword: {password}\n\nPlease login to complete your profile."
            mail.send(msg)
        except Exception as mail_err:
            print(f"Mail failed to send but user was created: {mail_err}")

        return jsonify({"message": "Registration successful. Welcome email sent!"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Database error: " + str(e)}), 500

# =========================
# ACCOUNT ACTIVATION
# =========================
@auth_bp.route("/activate", methods=["POST"])
def activate_account():
    data = request.get_json()
    token = data.get("token")
    new_password = data.get("password")

    if not token or not new_password:
        return jsonify({"error": "Token and password are required"}), 400

    user = User.query.filter_by(activation_token=token).first()
    if not user:
        return jsonify({"error": "Invalid or expired activation link"}), 400

    user.set_password(new_password)
    user.is_active = True
    user.activation_token = None
    db.session.commit()

    return jsonify({"message": "Account activated successfully. You can now log in."}), 200

# =========================
# FORGOT PASSWORD (OTP)
# =========================
@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    data = request.get_json()
    email = data.get("email")

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"error": "User with this email does not exist"}), 404

    # Generate 6-digit OTP
    otp = str(random.randint(100000, 999999))
    user.otp_code = otp
    user.otp_expiry = datetime.datetime.now() + datetime.timedelta(minutes=10) # 10 min expiry

    try:
        db.session.commit()

        # Send OTP via Email
        msg = Message("Your Password Reset OTP", recipients=[email])
        msg.body = f"Hello {user.name},\n\nYour OTP for password reset is: {otp}.\n\nThis code expires in 10 minutes."
        mail.send(msg)

        return jsonify({"message": "OTP sent to your email"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to send OTP: " + str(e)}), 500

# =========================
# RESET PASSWORD
# =========================
@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json()
    email = data.get("email")
    otp_received = data.get("otp")
    new_password = data.get("new_password")

    user = User.query.filter_by(email=email).first()

    if not user or user.otp_code != otp_received:
        return jsonify({"error": "Invalid OTP"}), 400

    if datetime.datetime.now() > user.otp_expiry:
        return jsonify({"error": "OTP has expired"}), 400

    try:
        # Update password and clear OTP
        user.set_password(new_password)
        user.otp_code = None
        user.otp_expiry = None
        db.session.commit()

        return jsonify({"message": "Password updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Update failed: " + str(e)}), 500

# =========================
# USER LOGIN
# =========================
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid credentials"}), 401

    if not user.is_active:
        return jsonify({"error": "Account not activated. Please check your email for the activation link."}), 403

    # Identity and Role claims
    access_token = create_access_token(
        identity=str(user.userId),
        additional_claims={"role": user.role}
    )

    response = jsonify({
        "message": "Login successful", 
        "role": user.role, 
        "name": user.name,
        "userId": user.userId
    })
    
    set_access_cookies(response, access_token)
    return response, 200

# =========================
# USER LOGOUT
# =========================
@auth_bp.route("/logout", methods=["POST"])
def logout():
    response = jsonify({"message": "Logout successful"})
    unset_jwt_cookies(response)
    return response, 200