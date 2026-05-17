# routes/visitor.py
from flask import Blueprint, jsonify, request
from models import db, Visitor
from datetime import datetime
visitor_bp = Blueprint('visitor', __name__)

@visitor_bp.route('/update-email', methods=['POST'])
def update_email():
    data = request.get_json()
    guest_id = request.cookies.get('guest_id')
    if not guest_id:
        return jsonify({'error': 'No session'}), 400
    visitor = Visitor.query.filter_by(guest_id=guest_id).first()
    if visitor:
        visitor.email = data.get('email', '')
        db.session.commit()
    return jsonify({'success': True})
