from flask import Blueprint, render_template, request, jsonify, current_app
from models import db, BlogPost, ImagePost, Journey, Visitor
from datetime import datetime
import uuid

main_bp = Blueprint('main', __name__)

# ── SILENT GLOBAL TRACKER ──────────────────────────────────────────
@main_bp.before_app_request
def track_visitor():
    # Do not track asset loads or your own admin actions
    if request.endpoint and (request.endpoint.startswith('static') or request.endpoint.startswith('admin')):
        return

    guest_id = request.cookies.get('guest_id')
    visitor = None

    if guest_id:
        visitor = Visitor.query.filter_by(guest_id=guest_id).first()
    
    if visitor:
        # Only update the DB if it's been more than 60 seconds to prevent spam
        if (datetime.utcnow() - visitor.last_visit).total_seconds() > 60:
            visitor.last_visit = datetime.utcnow()
            visitor.visit_count += 1
            db.session.commit()
    else:
        # 100% new visitor
        guest_id = str(uuid.uuid4())
        visitor = Visitor(
            guest_id=guest_id,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent', '')[:500]
        )
        db.session.add(visitor)
        db.session.commit()
        # Save ID to request so we can attach the cookie on the way out
        request.new_guest_id = guest_id

@main_bp.after_app_request
def set_visitor_cookie(response):
    if hasattr(request, 'new_guest_id'):
        response.set_cookie('guest_id', request.new_guest_id, max_age=60*60*24*365, httponly=True, samesite='Lax')
    return response
# ─────────────────────────────────────────────────────────────────

@main_bp.route('/')
def index():
    blogs = BlogPost.query.filter_by(is_published=True).order_by(BlogPost.created_at.desc()).limit(3).all()
    images = ImagePost.query.order_by(ImagePost.created_at.desc()).limit(6).all()
    journey_entries = Journey.query.order_by(Journey.order_index).all()

    # Grab the guest ID whether it's an old cookie or the brand new one we just generated
    current_guest_id = request.cookies.get('guest_id', getattr(request, 'new_guest_id', ''))

    return render_template('index.html',
                           blogs=blogs,
                           images=images,
                           journey_entries=journey_entries,
                           guest_id=current_guest_id,
                           profile_image_url=current_app.config.get('PROFILE_IMAGE_URL',''))

@main_bp.route('/api/stats')
def stats():
    return jsonify({
        'total_visitors': Visitor.query.count(),
        'total_blogs': BlogPost.query.filter_by(is_published=True).count(),
        'total_images': ImagePost.query.count(),
    })