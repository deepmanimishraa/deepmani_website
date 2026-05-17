from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
import cloudinary
import os

from config import Config
from models import db, Admin

login_manager = LoginManager()
mail         = Mail()
csrf         = CSRFProtect()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)

    login_manager.login_view        = 'admin.login'
    login_manager.login_message_category = 'info'

    # Safely configure cloudinary only if keys exist to prevent local crashes
    if app.config.get('CLOUDINARY_CLOUD_NAME'):
        cloudinary.config(
            cloud_name  = app.config.get('CLOUDINARY_CLOUD_NAME'),
            api_key     = app.config.get('CLOUDINARY_API_KEY'),
            api_secret  = app.config.get('CLOUDINARY_API_SECRET'),
        )

    # ── Blueprints ──────────────────────────────────────────
    from routes.main     import main_bp
    from routes.admin    import admin_bp
    from routes.blog     import blog_bp
    from routes.gallery  import gallery_bp
    from routes.journey  import journey_bp
    from routes.ai_chat  import ai_bp
    from routes.visitor  import visitor_bp
    from routes.messages import messages_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp,    url_prefix='/admin')
    app.register_blueprint(blog_bp,     url_prefix='/blog')
    app.register_blueprint(gallery_bp,  url_prefix='/gallery')
    app.register_blueprint(journey_bp,  url_prefix='/api/journey')
    app.register_blueprint(ai_bp,       url_prefix='/api/ai')
    app.register_blueprint(visitor_bp,  url_prefix='/api/visitor')
    app.register_blueprint(messages_bp, url_prefix='/api/messages')

    # ── Exempt JSON API blueprints from CSRF (they use fetch, not forms) ──
    csrf.exempt(gallery_bp)
    csrf.exempt(ai_bp)
    csrf.exempt(visitor_bp)
    csrf.exempt(messages_bp)
    csrf.exempt(journey_bp)

    @login_manager.user_loader
    def load_user(user_id):
        return Admin.query.get(int(user_id))

    with app.app_context():
        # TEMPORARY FIX: Drop the broken messages table so it can rebuild with the new columns
        from models import Message
        Message.__table__.drop(db.engine, checkfirst=True)
        
        db.create_all()
        _seed(app)

    return app


def _seed(app):
    from models import Admin, Journey
    
    # Create an admin securely using environment variables
    if not Admin.query.first():
        a = Admin(
            username=app.config.get('ADMIN_USERNAME'), 
            email=app.config.get('ADMIN_EMAIL')
        )
        a.set_password(app.config.get('ADMIN_PASSWORD'))
        db.session.add(a)

    # Create journey entries if none exist
    if not Journey.query.first():
        entries = [
            Journey(year='2022', title='Journey Begins',
                    description='Embarked on the path of knowledge and innovation. Started exploring Data Science & programming.',
                    icon='rocket', category='milestone', order_index=1),
            Journey(year='2023', title='IIT Madras — BS Data Science',
                    description='Enrolled in the prestigious BS in Data Science & Applications at IIT Madras. Deep-dived into Python, ML, and Statistical Analysis.',
                    icon='graduation', category='academic', order_index=2),
            Journey(year='2024', title='Founded PRAMANIIK',
                    description='Co-founded PRAMANIIK — a cybersecurity startup focused on data integrity and digital authentication. Leading innovation at the frontier of security.',
                    icon='shield', category='entrepreneurship', order_index=3),
            Journey(year='2025', title='Scaling & Vision',
                    description='Growing PRAMANIIK\'s footprint. Building scalable ecosystems to solve real-world problems. Making India the global leader in tech & AI.',
                    icon='globe', category='milestone', order_index=4),
        ]
        db.session.add_all(entries)

    db.session.commit()


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)