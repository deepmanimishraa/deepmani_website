# routes/journey.py
from flask import Blueprint, jsonify
from core.models import Journey
journey_bp = Blueprint('journey', __name__)

@journey_bp.route('/list')
def list_journey():
    entries = Journey.query.order_by(Journey.order_index).all()
    return jsonify([{
        'id': e.id, 'year': e.year, 'title': e.title,
        'description': e.description, 'icon': e.icon, 'category': e.category
    } for e in entries])
