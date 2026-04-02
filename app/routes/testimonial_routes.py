from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.testimonial import Testimonial
from app.models.user import User
from app.models.student import Student
from datetime import datetime

testimonial_bp = Blueprint('testimonial_bp', __name__, url_prefix='/testimonials')


@testimonial_bp.route('', methods=['GET'])
@jwt_required()
def get_testimonials():
    testimonials = Testimonial.query\
        .order_by(Testimonial.is_featured.desc(), Testimonial.date_added.desc())\
        .all()

    result = []
    for t in testimonials:
        student = Student.query.filter_by(userId=t.userId).first()
        profile_image = None
        import os
        if t.user and t.user.profile_image:
            profile_image = t.user.profile_image
        result.append({
            'id':          t.id,
            'userId':      t.userId,
            'content':     t.content,
            'date_added':  t.date_added.strftime('%b %d, %Y'),
            'is_featured': t.is_featured,
            'user_name':   t.user.name if t.user else 'Unknown',
            'department':  student.department if student else '',
            'roll_no':     student.rollNumber if student else '',
            'profile_image': profile_image
        })
    return jsonify(result), 200


@testimonial_bp.route('', methods=['POST'])
@jwt_required()
def add_testimonial():
    user_id = get_jwt_identity()
    data = request.get_json()
    content = (data.get('content') or '').strip()

    if not content:
        return jsonify({'message': 'Content is required.'}), 400
    if len(content) > 1000:
        return jsonify({'message': 'Testimonial must be under 1000 characters.'}), 400

    # One testimonial per student
    existing = Testimonial.query.filter_by(userId=user_id).first()
    if existing:
        return jsonify({'message': 'You have already posted a testimonial. Edit it instead.'}), 409

    t = Testimonial(userId=user_id, content=content)
    db.session.add(t)
    db.session.commit()
    return jsonify({'message': 'Testimonial posted successfully!', 'id': t.id}), 201


@testimonial_bp.route('/<int:testi_id>', methods=['PUT'])
@jwt_required()
def edit_testimonial(testi_id):
    user_id = get_jwt_identity()
    t = Testimonial.query.get_or_404(testi_id)

    if t.userId != user_id:
        return jsonify({'message': 'Unauthorized.'}), 403

    data = request.get_json()
    content = (data.get('content') or '').strip()
    if not content:
        return jsonify({'message': 'Content is required.'}), 400
    if len(content) > 1000:
        return jsonify({'message': 'Testimonial must be under 1000 characters.'}), 400

    t.content = content
    t.date_added = datetime.utcnow()
    db.session.commit()
    return jsonify({'message': 'Testimonial updated.'}), 200


@testimonial_bp.route('/<int:testi_id>', methods=['DELETE'])
@jwt_required()
def delete_testimonial(testi_id):
    user_id = get_jwt_identity()
    t = Testimonial.query.get_or_404(testi_id)

    if t.userId != user_id:
        return jsonify({'message': 'Unauthorized.'}), 403

    db.session.delete(t)
    db.session.commit()
    return jsonify({'message': 'Testimonial deleted.'}), 200
