# routes/blog.py
from flask import Blueprint, render_template, abort, request
from models import db, BlogPost
import markdown as md

blog_bp = Blueprint('blog', __name__)

@blog_bp.route('/')
def list_blogs():
    page = request.args.get('page', 1, type=int)
    posts = BlogPost.query.filter_by(is_published=True).order_by(BlogPost.created_at.desc()).paginate(page=page, per_page=9)
    return render_template('blog/list.html', posts=posts)

@blog_bp.route('/<slug>')
def post(slug):
    post = BlogPost.query.filter_by(slug=slug, is_published=True).first_or_404()
    post.views += 1
    db.session.commit()
    content_html = md.markdown(post.content, extensions=['fenced_code', 'tables', 'toc'])
    return render_template('blog/post.html', post=post, content_html=content_html)
