import os
import cloudinary
from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from dotenv import load_dotenv

# 1. Load environment variables
load_dotenv()

# 2. Import the database object from your models.py
from .models import db

# 3. Initialize other Plugins globally
login_manager = LoginManager()
mail = Mail()
csrf = CSRFProtect()

def create_app():
    # Tell Flask to look in the core folder for templates and static files
    app = Flask(__name__, template_folder='templates', static_folder='static')
    
    # Load configuration
    from .config import Config
    app.config.from_object(Config)

    # Bind Plugins to the app
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = 'admin.login'
    login_manager.login_message_category = 'info'

    cloudinary.config(
        cloud_name  = app.config.get('CLOUDINARY_CLOUD_NAME'),
        api_key     = app.config.get('CLOUDINARY_API_KEY'),
        api_secret  = app.config.get('CLOUDINARY_API_SECRET'),
    )

    # Register Blueprints inside the app context
    with app.app_context():
        from .routes.main     import main_bp
        from .routes.admin    import admin_bp
        from .routes.blog     import blog_bp
        from .routes.gallery  import gallery_bp
        from .routes.journey  import journey_bp
        from .routes.ai_chat  import ai_bp
        from .routes.visitor  import visitor_bp
        from .routes.messages import messages_bp

        app.register_blueprint(main_bp)
        app.register_blueprint(admin_bp,    url_prefix='/admin')
        app.register_blueprint(blog_bp,     url_prefix='/blog')
        app.register_blueprint(gallery_bp,  url_prefix='/gallery')
        app.register_blueprint(journey_bp,  url_prefix='/api/journey')
        app.register_blueprint(ai_bp,       url_prefix='/api/ai')
        app.register_blueprint(visitor_bp,  url_prefix='/api/visitor')
        app.register_blueprint(messages_bp, url_prefix='/api/messages')

        # Exempt JSON API blueprints from CSRF
        csrf.exempt(gallery_bp)
        csrf.exempt(ai_bp)
        csrf.exempt(visitor_bp)
        csrf.exempt(messages_bp)
        csrf.exempt(journey_bp)

        from .models import Admin, Journey

        @login_manager.user_loader
        def load_user(user_id):
            return Admin.query.get(int(user_id))

        db.create_all()
        _seed(app, Admin, Journey)

    return app

def _seed(app, Admin, Journey):
    if not Admin.query.first():
        a = Admin(
            username=app.config.get('SEED_ADMIN_USERNAME'), 
            email=app.config.get('SEED_ADMIN_EMAIL')
        )
        # Avoid crashing if passwords aren't set in .env yet
        seed_pass = app.config.get('SEED_ADMIN_PASSWORD')
        if seed_pass:
            a.set_password(seed_pass)
            db.session.add(a)

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