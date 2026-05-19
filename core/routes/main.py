from flask import Blueprint, render_template, request, jsonify
from core.models import db, BlogPost, ImagePost, Journey, Visitor
from datetime import datetime
import uuid

main_bp = Blueprint('main', __name__)

def get_or_create_visitor():
    guest_id = request.cookies.get('guest_id')
    visitor = None
    if guest_id:
        visitor = Visitor.query.filter_by(guest_id=guest_id).first()
        if visitor:
            visitor.last_visit = datetime.utcnow()
            visitor.visit_count += 1
            db.session.commit()
    if not visitor:
        guest_id = str(uuid.uuid4())
        visitor = Visitor(
            guest_id=guest_id,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')[:500]
        )
        db.session.add(visitor)
        db.session.commit()
    return visitor, guest_id

@main_bp.route('/')
def index():
    visitor, guest_id = get_or_create_visitor()
    blogs = BlogPost.query.filter_by(is_published=True).order_by(BlogPost.created_at.desc()).limit(3).all()
    images = ImagePost.query.order_by(ImagePost.created_at.desc()).limit(6).all()
    journey_entries = Journey.query.order_by(Journey.order_index).all()

    from flask import current_app
    resp = render_template('index.html',
                           blogs=blogs,
                           images=images,
                           journey_entries=journey_entries,
                           guest_id=guest_id,
                           profile_image_url=current_app.config.get('PROFILE_IMAGE_URL',''))
    from flask import make_response
    response = make_response(resp)
    response.set_cookie('guest_id', guest_id, max_age=60*60*24*365, httponly=True, samesite='Lax')
    return response

@main_bp.route('/api/stats')
def stats():
    return jsonify({
        'total_visitors': Visitor.query.count(),
        'total_blogs': BlogPost.query.filter_by(is_published=True).count(),
        'total_images': ImagePost.query.count(),
    })
