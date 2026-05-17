from flask import Blueprint, jsonify, request
from models import db, ImagePost, Like, Comment

gallery_bp = Blueprint('gallery', __name__)

# ── All these are JSON APIs called by fetch() — exempt from form CSRF ──
@gallery_bp.route('/api/list')
def gallery_list():
    page = request.args.get('page', 1, type=int)
    per_page = 12
    imgs = ImagePost.query.order_by(ImagePost.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False)
    guest_id = request.cookies.get('guest_id', '')
    data = []
    for img in imgs.items:
        liked = Like.query.filter_by(
            image_post_id=img.id, visitor_id=guest_id).first() is not None
        data.append({
            'id':          img.id,
            'title':       img.title or '',
            'description': img.description or '',
            'url':         img.image_url,
            'taken_at':    str(img.taken_at) if img.taken_at else '',
            'likes':       len(img.likes),
            'comments':    len(img.comments),
            'liked':       liked,
        })
    return jsonify({'images': data, 'has_next': imgs.has_next, 'page': page})


@gallery_bp.route('/api/like/<int:img_id>', methods=['POST'])
def toggle_like(img_id):
    guest_id = request.cookies.get('guest_id')
    if not guest_id:
        return jsonify({'error': 'No guest ID'}), 403
    img = ImagePost.query.get_or_404(img_id)
    existing = Like.query.filter_by(
        image_post_id=img_id, visitor_id=guest_id).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        liked = False
    else:
        like = Like(image_post_id=img_id, visitor_id=guest_id)
        db.session.add(like)
        db.session.commit()
        liked = True
    count = Like.query.filter_by(image_post_id=img_id).count()
    return jsonify({'liked': liked, 'count': count})


@gallery_bp.route('/api/comment/<int:img_id>', methods=['POST'])
def add_comment(img_id):
    data = request.get_json(silent=True) or {}
    guest_id = request.cookies.get('guest_id', '')
    content = (data.get('content') or '').strip()[:1000]
    if not content:
        return jsonify({'error': 'Empty comment'}), 400
    comment = Comment(
        content=content,
        author_name=(data.get('name') or 'Anonymous').strip()[:100],
        author_email=(data.get('email') or '').strip()[:120],
        visitor_id=guest_id or None,
        image_post_id=img_id,
    )
    db.session.add(comment)
    db.session.commit()
    return jsonify({
        'success': True,
        'comment': {
            'name':    comment.author_name,
            'content': comment.content,
            'date':    comment.created_at.strftime('%b %d, %Y'),
        }
    })


@gallery_bp.route('/api/comments/<int:img_id>')
def get_comments(img_id):
    comments = (Comment.query
                .filter_by(image_post_id=img_id, is_approved=True)
                .order_by(Comment.created_at.desc())
                .all())
    return jsonify({'comments': [
        {'name': c.author_name, 'content': c.content,
         'date': c.created_at.strftime('%b %d, %Y')}
        for c in comments
    ]})
