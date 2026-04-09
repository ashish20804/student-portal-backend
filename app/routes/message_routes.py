from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db, mail
from app.models.message import Message
from app.models.user import User
from app.models.student import Student
from sqlalchemy import or_
from flask_mail import Message as MailMessage
from datetime import datetime, timedelta
import base64, threading, logging

message_bp = Blueprint("message", __name__, url_prefix="/message")

def _profile_image_url(image_bytes):
    """Convert MEDIUMBLOB bytes to base64 data URL, or return None."""
    if not image_bytes:
        return None
    try:
        import base64 as b64
        encoded = b64.b64encode(image_bytes).decode('utf-8')
        return f"data:image/jpeg;base64,{encoded}"
    except Exception:
        return None

def _decode_content(encoded):
    """Decode Base64 message content sent from frontend."""
    try:
        return base64.b64decode(encoded).decode('utf-8')
    except Exception:
        return encoded  # fallback: return as-is if not encoded

def _build_email_html(receiver_name, sender_name, sender_role, sender_identifier, preview, timestamp, frontend_url):
    """Build a styled HTML email body for message notification."""
    role_badge_color = {
        'faculty': '#0d6efd',
        'admin':   '#dc3545',
        'student': '#198754'
    }.get(sender_role, '#6c757d')
    role_label = sender_role.capitalize()
    identifier_line = f'<p style="margin:0;font-size:13px;color:#6c757d;">{sender_identifier}</p>' if sender_identifier else ''
    preview_escaped = preview[:300].replace('<', '&lt;').replace('>', '&gt;')
    ellipsis = '...' if len(preview) > 300 else ''

    return f"""
    <!DOCTYPE html>
    <html>
    <body style="margin:0;padding:0;background:#f4f6f9;font-family:'Segoe UI',Arial,sans-serif;">
      <table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f6f9;padding:30px 0;">
        <tr><td align="center">
          <table width="520" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 2px 12px rgba(0,0,0,0.08);">

            <!-- Header -->
            <tr>
              <td style="background:linear-gradient(135deg,#0d6efd,#6610f2);padding:28px 32px;text-align:center;">
                <p style="margin:0;font-size:22px;font-weight:700;color:#fff;">&#128172; New Message</p>
                <p style="margin:6px 0 0;font-size:13px;color:rgba(255,255,255,0.8);">Student Portal Notification</p>
              </td>
            </tr>

            <!-- Body -->
            <tr>
              <td style="padding:28px 32px;">
                <p style="margin:0 0 20px;font-size:15px;color:#333;">Hi <strong>{receiver_name}</strong>,</p>
                <p style="margin:0 0 20px;font-size:14px;color:#555;">You have received a new message on the Student Portal.</p>

                <!-- Sender card -->
                <table width="100%" cellpadding="0" cellspacing="0" style="background:#f8f9fa;border-radius:10px;padding:16px;margin-bottom:20px;">
                  <tr>
                    <td style="width:44px;vertical-align:top;">
                      <div style="width:44px;height:44px;border-radius:50%;background:{role_badge_color};color:#fff;font-size:18px;font-weight:700;text-align:center;line-height:44px;">{sender_name[0].upper()}</div>
                    </td>
                    <td style="padding-left:12px;vertical-align:middle;">
                      <p style="margin:0;font-size:15px;font-weight:700;color:#212529;">{sender_name}</p>
                      {identifier_line}
                      <span style="display:inline-block;margin-top:4px;padding:2px 10px;background:{role_badge_color};color:#fff;border-radius:20px;font-size:11px;font-weight:600;">{role_label}</span>
                    </td>
                  </tr>
                </table>

                <!-- Message preview -->
                <div style="border-left:4px solid #0d6efd;background:#f0f4ff;border-radius:0 8px 8px 0;padding:14px 16px;margin-bottom:24px;">
                  <p style="margin:0 0 6px;font-size:11px;font-weight:600;color:#0d6efd;text-transform:uppercase;letter-spacing:0.5px;">Message Preview</p>
                  <p style="margin:0;font-size:14px;color:#333;line-height:1.6;">&ldquo;{preview_escaped}{ellipsis}&rdquo;</p>
                </div>

                <p style="margin:0 0 6px;font-size:12px;color:#aaa;">Received at {timestamp}</p>

                <!-- CTA -->
                <div style="text-align:center;margin-top:24px;">
                  <a href="{frontend_url}/messages.html" style="display:inline-block;background:linear-gradient(135deg,#0d6efd,#6610f2);color:#fff;text-decoration:none;padding:12px 32px;border-radius:8px;font-size:14px;font-weight:600;">&#128172; Open Messages</a>
                </div>
              </td>
            </tr>

            <!-- Footer -->
            <tr>
              <td style="background:#f8f9fa;padding:16px 32px;text-align:center;border-top:1px solid #e9ecef;">
                <p style="margin:0;font-size:11px;color:#aaa;">This is an automated notification from Student Portal. Do not reply to this email.</p>
              </td>
            </tr>

          </table>
        </td></tr>
      </table>
    </body>
    </html>
    """

def _send_notification_async(app, receiver_email, receiver_name, sender_name,
                              sender_role, sender_identifier, preview, timestamp):
    """Send HTML email notification in a background thread."""
    def run():
        with app.app_context():
            try:
                from app.email_utils import send_email_async
                frontend_url = app.config.get('FRONTEND_URL', 'https://student-portal-backend-8icb.onrender.com').rstrip('/')
                subject = f"\U0001f4ac New message from {sender_name} | Student Portal"
                html_body = _build_email_html(
                    receiver_name, sender_name, sender_role,
                    sender_identifier, preview, timestamp, frontend_url
                )
                plain_body = (
                    f"Hi {receiver_name},\n\n"
                    f"You have a new message from {sender_name} ({sender_role}) on the Student Portal.\n\n"
                    f"Preview: \"{preview[:200]}{'...' if len(preview) > 200 else ''}\"\n\n"
                    f"Open messages: {frontend_url}/messages.html\n\n"
                    f"---\nThis is an automated notification. Do not reply."
                )
                msg = MailMessage(
                    subject=subject,
                    recipients=[receiver_email],
                    body=plain_body,
                    html=html_body
                )
                mail.send(msg)
                logging.info(f"Message notification sent to {receiver_email}")
            except Exception as e:
                logging.warning(f"Email notification failed: {e}")
    threading.Thread(target=run, daemon=True).start()

@message_bp.route("/send", methods=["POST"])
@jwt_required()
def send_message():
    from flask import current_app
    sender_id = int(get_jwt_identity())
    data = request.get_json()
    receiver_id = data.get("receiverId")
    content = data.get("content")

    if not receiver_id or not content:
        return jsonify({"message": "receiverId and content required"}), 400

    new_message = Message(senderId=sender_id, receiverId=receiver_id, content=content)
    db.session.add(new_message)
    db.session.commit()

    # --- Email notification (only if no message sent in last 10 minutes) ---
    cutoff = datetime.utcnow() - timedelta(minutes=10)
    recent = Message.query.filter(
        Message.senderId == sender_id,
        Message.receiverId == receiver_id,
        Message.messageId != new_message.messageId,
        Message.timestamp >= cutoff
    ).first()

    if not recent:
        receiver = User.query.get(receiver_id)
        sender   = User.query.get(sender_id)
        if receiver and receiver.email and sender:
            plain_text = _decode_content(content)
            # Build sender identifier: roll number for students, email for faculty/admin
            sender_student = Student.query.filter_by(userId=sender_id).first()
            if sender_student and sender_student.rollNumber:
                sender_identifier = f"Roll No: {sender_student.rollNumber}"
            else:
                sender_identifier = sender.email
            timestamp = datetime.utcnow().strftime("%d %b %Y, %I:%M %p") + " UTC"
            _send_notification_async(
                current_app._get_current_object(),
                receiver.email,
                receiver.name,
                sender.name,
                sender.role,
                sender_identifier,
                plain_text,
                timestamp
            )

    return jsonify({"message": "Message sent successfully"}), 201

@message_bp.route("/unread-count", methods=["GET"])
@jwt_required()
def unread_count():
    from sqlalchemy import func
    user_id = int(get_jwt_identity())

    # Get all senders who sent messages to this user
    senders = db.session.query(Message.senderId, func.max(Message.timestamp).label('last_sent'))\
        .filter(Message.receiverId == user_id)\
        .group_by(Message.senderId).all()

    unread_senders = []
    for sender_id, last_sent in senders:
        # Unread = sender's last message is newer than user's last reply to them
        last_reply = db.session.query(func.max(Message.timestamp))\
            .filter(Message.senderId == user_id, Message.receiverId == sender_id).scalar()
        if last_reply is None or last_sent > last_reply:
            sender  = User.query.get(sender_id)
            student = Student.query.filter_by(userId=sender_id).first()
            if sender:
                unread_senders.append({
                    'userId':     sender_id,
                    'name':       sender.name,
                    'role':       sender.role,
                    'identifier': student.rollNumber if student else sender.email,
                    'time':       last_sent.strftime('%I:%M %p'),
                    'ts':         last_sent.isoformat()   # ISO for client-side comparison
                })

    return jsonify({'count': len(unread_senders), 'senders': unread_senders}), 200


@message_bp.route("/chats", methods=["GET"])
@jwt_required()
def get_recent_chats():
    user_id = int(get_jwt_identity())
    
    # Identify all users who have exchanged messages with the current user
    sent_to = db.session.query(Message.receiverId).filter(Message.senderId == user_id).distinct()
    received_from = db.session.query(Message.senderId).filter(Message.receiverId == user_id).distinct()
    
    contact_ids = set([r[0] for r in sent_to.all()] + [r[0] for r in received_from.all()])
    
    # Outer join with Student to get rollNumber (if they are a student)
    # Profile image and Name are pulled directly from the User table
    contacts = db.session.query(User, Student.rollNumber).outerjoin(
        Student, User.userId == Student.userId
    ).filter(User.userId.in_(contact_ids)).all()
    
    result = []
    for user_obj, roll_no in contacts:
        result.append({
            "userId":        user_obj.userId,
            "username":      user_obj.name,
            "role":          user_obj.role,
            "profile_image": _profile_image_url(user_obj.profile_image),
            "rollNumber":    roll_no or ""
        })
    return jsonify(result), 200

@message_bp.route("/search", methods=["GET"])
@jwt_required()
def search_users():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify([]), 200

    # Search logic: Checks User.name OR Student.rollNumber
    search_results = db.session.query(User, Student.rollNumber).outerjoin(
        Student, User.userId == Student.userId
    ).filter(
        or_(
            User.name.like(f"%{query}%"),
            Student.rollNumber.like(f"%{query}%")
        )
    ).limit(15).all()

    result = []
    for user_obj, roll_no in search_results:
        result.append({
            "userId":        user_obj.userId,
            "username":      user_obj.name,
            "role":          user_obj.role,
            "profile_image": _profile_image_url(user_obj.profile_image),
            "rollNumber":    roll_no or ""
        })
    return jsonify(result), 200

@message_bp.route("/conversation/<int:other_user_id>", methods=["GET"])
@jwt_required()
def get_conversation(other_user_id):
    user_id = int(get_jwt_identity())

    messages = Message.query.filter(
        or_(
            (Message.senderId == user_id) & (Message.receiverId == other_user_id),
            (Message.senderId == other_user_id) & (Message.receiverId == user_id)
        )
    ).order_by(Message.timestamp.asc()).all()

    return jsonify([{
        "messageId": m.messageId,
        "senderId": m.senderId,
        "content": m.content,
        "timestamp": m.timestamp.strftime("%I:%M %p")
    } for m in messages]), 200