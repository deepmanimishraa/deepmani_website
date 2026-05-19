from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from core.models import db, Admin, BlogPost, ImagePost, Journey, Visitor, Message, Comment, Like
from slugify import slugify
from datetime import datetime, timedelta
import cloudinary.uploader

admin_bp = Blueprint('admin', __name__)

# ─── AUTH ───────────────────────────────────────────────────
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    if request.method == 'POST':
        admin = Admin.query.filter_by(username=request.form.get('username')).first()
        if admin and admin.check_password(request.form.get('password', '')):
            login_user(admin)
            return redirect(url_for('admin.dashboard'))
        flash('Invalid credentials', 'danger')
    return render_template('admin/login.html')

@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

# ─── DASHBOARD ──────────────────────────────────────────────
# ─── DASHBOARD ──────────────────────────────────────────────
@admin_bp.route('/dashboard')
@login_required
def dashboard():
    try:
        thirty = datetime.utcnow() - timedelta(days=30)
        seven  = datetime.utcnow() - timedelta(days=7)

        # 🛠️ FIX 3: Bulletproof PostgreSQL Date Extraction using explicit db wrappers
        daily_visitors = (db.session.query(
                db.cast(Visitor.first_visit, db.Date).label('v_date'),
                db.func.count(Visitor.id).label('v_count'))
            .filter(Visitor.first_visit >= thirty)
            .group_by(db.cast(Visitor.first_visit, db.Date))
            .all())

        stats = {
            'visitors':        Visitor.query.count(),
            'blogs':           BlogPost.query.count(),
            'images':          ImagePost.query.count(),
            'messages':        Message.query.filter_by(is_read=False).count(),
            'comments':        Comment.query.count(),
            'likes':           Like.query.count(),
            'new_visitors_7d': Visitor.query.filter(Visitor.first_visit >= seven).count(),
            'recent_visitors': Visitor.query.order_by(Visitor.last_visit.desc()).limit(8).all(),
            'recent_messages': Message.query.order_by(Message.created_at.desc()).limit(5).all(),
            'daily_visitors':  [{'date': str(d.v_date), 'count': d.v_count} for d in daily_visitors],
        }
        return render_template('admin/dashboard.html', stats=stats)
        
    except Exception as e:
        # 🛠️ DIAGNOSTIC TRAP: Prints the exact crash error to your screen instead of a white 500 page
        import traceback
        return f"<div style='color:#ff6b6b; background:#111; padding:3rem; font-family:monospace; height:100vh; overflow:auto;'><h2>Dashboard Crash Report</h2><pre>{traceback.format_exc()}</pre></div>"

# ─── BLOG ───────────────────────────────────────────────────
@admin_bp.route('/blogs')
@login_required
def blogs():
    posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
    return render_template('admin/manage_blogs.html', posts=posts)

@admin_bp.route('/blogs/new', methods=['GET', 'POST'])
@login_required
def new_blog():
    if request.method == 'POST':
        title      = request.form.get('title', '').strip()
        content    = request.form.get('content', '').strip()
        excerpt    = request.form.get('excerpt', '')[:500]
        tags       = request.form.get('tags', '')
        cover_url  = request.form.get('cover_image_url', '')
        published  = request.form.get('is_published') == 'on'

        slug = slugify(title)
        base, n = slug, 1
        while BlogPost.query.filter_by(slug=slug).first():
            slug = f"{base}-{n}"; n += 1

        if 'cover_file' in request.files and request.files['cover_file'].filename:
            res = cloudinary.uploader.upload(
                request.files['cover_file'], folder='deepmani/blogs')
            cover_url = res['secure_url']

        db.session.add(BlogPost(title=title, slug=slug, content=content,
                                excerpt=excerpt, tags=tags,
                                cover_image_url=cover_url, is_published=published))
        db.session.commit()
        flash('Blog post created!', 'success')
        return redirect(url_for('admin.blogs'))
    return render_template('admin/blog_form.html', post=None)

@admin_bp.route('/blogs/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_blog(post_id):
    post = BlogPost.query.get_or_404(post_id)
    if request.method == 'POST':
        post.title        = request.form.get('title', '').strip()
        post.content      = request.form.get('content', '').strip()
        post.excerpt      = request.form.get('excerpt', '')[:500]
        post.tags         = request.form.get('tags', '')
        post.is_published = request.form.get('is_published') == 'on'
        post.updated_at   = datetime.utcnow()
        if 'cover_file' in request.files and request.files['cover_file'].filename:
            res = cloudinary.uploader.upload(
                request.files['cover_file'], folder='deepmani/blogs')
            post.cover_image_url = res['secure_url']
        db.session.commit()
        flash('Blog post updated!', 'success')
        return redirect(url_for('admin.blogs'))
    return render_template('admin/blog_form.html', post=post)

@admin_bp.route('/blogs/delete/<int:post_id>', methods=['POST'])
@login_required
def delete_blog(post_id):
    post = BlogPost.query.get_or_404(post_id)
    db.session.delete(post); db.session.commit()
    flash('Blog post deleted.', 'success')
    return redirect(url_for('admin.blogs'))

# ─── GALLERY ────────────────────────────────────────────────
@admin_bp.route('/gallery')
@login_required
def gallery():
    images = ImagePost.query.order_by(ImagePost.created_at.desc()).all()
    return render_template('admin/manage_gallery.html', images=images)

@admin_bp.route('/gallery/upload', methods=['POST'])
@login_required
def upload_image():
    if 'image' not in request.files or not request.files['image'].filename:
        return jsonify({'error': 'No file selected'}), 400
    taken_at_str = request.form.get('taken_at', '')
    taken_at     = None
    if taken_at_str:
        try:
            taken_at = datetime.strptime(taken_at_str, '%Y-%m-%d').date()
        except ValueError:
            pass
    res = cloudinary.uploader.upload(
        request.files['image'], folder='deepmani/gallery',
        transformation=[{'width': 600, 'height': 800, 'crop': 'fill', 'gravity': 'auto'}])
    img = ImagePost(
        title=request.form.get('title', '').strip(),
        description=request.form.get('description', '').strip(),
        image_url=res['secure_url'],
        cloudinary_public_id=res['public_id'],
        taken_at=taken_at,
    )
    db.session.add(img); db.session.commit()
    return jsonify({'success': True, 'url': res['secure_url']})

@admin_bp.route('/gallery/delete/<int:img_id>', methods=['POST'])
@login_required
def delete_image(img_id):
    img = ImagePost.query.get_or_404(img_id)
    if img.cloudinary_public_id:
        try:
            cloudinary.uploader.destroy(img.cloudinary_public_id)
        except Exception:
            pass
    db.session.delete(img); db.session.commit()
    flash('Image deleted.', 'success')
    return redirect(url_for('admin.gallery'))

# ─── JOURNEY ────────────────────────────────────────────────
@admin_bp.route('/journey')
@login_required
def journey():
    entries = Journey.query.order_by(Journey.order_index).all()
    return render_template('admin/manage_journey.html', entries=entries)

@admin_bp.route('/journey/new', methods=['POST'])
@login_required
def new_journey():
    db.session.add(Journey(
        year=request.form.get('year', '').strip(),
        title=request.form.get('title', '').strip(),
        description=request.form.get('description', '').strip(),
        icon=request.form.get('icon', 'star'),
        category=request.form.get('category', 'achievement'),
        order_index=Journey.query.count() + 1,
    ))
    db.session.commit()
    flash('Journey entry added!', 'success')
    return redirect(url_for('admin.journey'))

@admin_bp.route('/journey/edit/<int:eid>', methods=['POST'])
@login_required
def edit_journey(eid):
    e = Journey.query.get_or_404(eid)
    e.year        = request.form.get('year', '').strip()
    e.title       = request.form.get('title', '').strip()
    e.description = request.form.get('description', '').strip()
    e.icon        = request.form.get('icon', 'star')
    e.category    = request.form.get('category', 'achievement')
    db.session.commit()
    flash('Journey entry updated!', 'success')
    return redirect(url_for('admin.journey'))

@admin_bp.route('/journey/delete/<int:eid>', methods=['POST'])
@login_required
def delete_journey(eid):
    db.session.delete(Journey.query.get_or_404(eid)); db.session.commit()
    flash('Journey entry deleted.', 'success')
    return redirect(url_for('admin.journey'))

# ─── MESSAGES ────────────────────────────────────────────────
@admin_bp.route('/messages')
@login_required
def messages():
    msgs = Message.query.order_by(Message.created_at.desc()).all()
    Message.query.filter_by(is_read=False).update({'is_read': True})
    db.session.commit()
    return render_template('admin/messages.html', messages=msgs)

@admin_bp.route('/messages/reply/<int:msg_id>', methods=['POST'])
@login_required
def reply_message(msg_id):
    from threading import Thread
    from core import mail
    from flask_mail import Message as MailMessage
    from flask import current_app
    
    msg        = Message.query.get_or_404(msg_id)
    reply_text = request.form.get('reply', '').strip()
    mail_user  = current_app.config.get('MAIL_USERNAME')
    
    # 1. Prepare the email
    email_msg = MailMessage(
        subject=f"Re: {msg.subject or 'Your message to Deepmani'}",
        sender=mail_user,
        recipients=[msg.sender_email],
        body=(
            f"Hi {msg.sender_name},\n\n{reply_text}\n\n"
            "—\nDeepmani Mishraa\nCo-Founder, PRAMANIIK | IIT Madras"
        )
    )
    
    # 2. Define the background worker
    def send_async_reply(app, email_to_send):
        with app.app_context():
            try:
                mail.send(email_to_send)
            except Exception as e:
                print(f"\n🔥 ADMIN REPLY ERROR: {str(e)}\n")

    # 3. 🚀 Fire and Forget!
    app = current_app._get_current_object()
    Thread(target=send_async_reply, args=(app, email_msg)).start()
    
    # 4. Instantly update DB and return to dashboard
    msg.reply_sent = True
    db.session.commit()
    flash('Reply sent!', 'success')
    
    return redirect(url_for('admin.messages'))

# ─── ANALYTICS ───────────────────────────────────────────────
# ─── ANALYTICS ───────────────────────────────────────────────
@admin_bp.route('/analytics')
@login_required
def analytics():
    from sqlalchemy import func, cast, Date
    thirty = datetime.utcnow() - timedelta(days=30)

    # 🛠️ Universal Date Extraction
    daily = (db.session.query(
            cast(Visitor.first_visit, Date).label('date'),
            func.count(Visitor.id).label('count'))
        .filter(Visitor.first_visit >= thirty)
        .group_by(cast(Visitor.first_visit, Date))
        .order_by(cast(Visitor.first_visit, Date))
        .all())

    blog_views = BlogPost.query.order_by(BlogPost.views.desc()).limit(8).all()

    content_data = {
        'blogs':    BlogPost.query.count(),
        'images':   ImagePost.query.count(),
        'comments': Comment.query.count(),
        'likes':    Like.query.count(),
        'messages': Message.query.count(),
        'visitors': Visitor.query.count(),
    }

    journey_cats = (db.session.query(
            Journey.category, func.count(Journey.id))
        .group_by(Journey.category).all())

    returning = Visitor.query.filter(Visitor.visit_count > 1).count()
    new_v     = Visitor.query.filter(Visitor.visit_count == 1).count()

    # 🛠️ Safer SQLite detection for hourly chart
    is_sqlite = db.engine.name == 'sqlite'
    hourly = (db.session.query(
            func.strftime('%H', Visitor.first_visit).label('hour'),
            func.count(Visitor.id).label('count'))
        .group_by(func.strftime('%H', Visitor.first_visit))
        .all()) if is_sqlite else (
        db.session.query(
            func.extract('hour', Visitor.first_visit).label('hour'),
            func.count(Visitor.id).label('count'))
        .group_by(func.extract('hour', Visitor.first_visit))
        .all())

    stats = {
        'total_visitors': content_data['visitors'],
        'total_blogs':    content_data['blogs'],
        'total_images':   content_data['images'],
        'total_messages': content_data['messages'],
        'total_likes':    content_data['likes'],
        'total_comments': content_data['comments'],
        'daily_visitors': [{'date': str(d.date), 'count': d.count} for d in daily],
        'top_blogs':      blog_views,
        'content_data':   content_data,
        'returning':      returning,
        'new_visitors':   new_v,
        'hourly':         [{'hour': int(h.hour or 0), 'count': h.count} for h in hourly],
        'journey_cats':   [{'cat': c, 'count': n} for c, n in journey_cats],
    }
    return render_template('admin/analytics.html', stats=stats)



# ─── DATABASE MEDIC ROUTE (Temporary) ───────────────────────
@admin_bp.route('/fix-db')
def fix_db():
    from sqlalchemy import text
    try:
        # Surgically inject missing columns into the live Postgres database
        queries = [
            "ALTER TABLE comments ADD COLUMN IF NOT EXISTS author_email VARCHAR(120);",
            "ALTER TABLE messages ADD COLUMN IF NOT EXISTS reply_sent BOOLEAN DEFAULT FALSE;",
            "ALTER TABLE messages ADD COLUMN IF NOT EXISTS visitor_id VARCHAR(64);",
            "ALTER TABLE visitors ADD COLUMN IF NOT EXISTS email VARCHAR(120);",
            "ALTER TABLE image_posts ADD COLUMN IF NOT EXISTS cloudinary_public_id VARCHAR(300);"
        ]
        for q in queries:
            db.session.execute(text(q))
            
        db.session.commit()
        return "<h2 style='color: #40E0D0; background: #111; padding: 2rem;'>SUCCESS! 🚀<br>Database patched. You can now go to /admin/dashboard</h2>"
        
    except Exception as e:
        db.session.rollback()
        return f"<h2 style='color: #ff6b6b; background: #111; padding: 2rem;'>Error: {str(e)}</h2>"