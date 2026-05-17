"""
config.py — All configuration loaded from environment variables.
Never hardcode secrets here. Use .env for local dev (see .env.example).
"""
import os
from dotenv import load_dotenv

# Ensure we get the absolute path to the current directory
basedir = os.path.abspath(os.path.dirname(__file__))

# loads .env file in local dev; on Render, env vars come from dashboard
load_dotenv(os.path.join(basedir, '.env')) 

class Config:
    # ── Core ────────────────────────────────────────────────
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'change-this-before-deploying'

    # ── Database ─────────────────────────────────────────────
    # Fallback safely to a local sqlite database in the project folder
    _db_url = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'dev.db')
    
    # Render uses postgres:// but SQLAlchemy 1.4+ needs postgresql://
    if _db_url.startswith('postgres://'):
        _db_url = _db_url.replace('postgres://', 'postgresql://', 1)
        
    # FIX: This must exactly be named SQLALCHEMY_DATABASE_URI
    SQLALCHEMY_DATABASE_URI        = _db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS      = {'pool_pre_ping': True}

    # ── Cloudinary ───────────────────────────────────────────
    CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME')
    CLOUDINARY_API_KEY    = os.environ.get('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET')

    # ── Google Gemini AI ─────────────────────────────────────
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

    # ── Email (Flask-Mail via Gmail SMTP) ────────────────────
    MAIL_SERVER         = 'smtp.gmail.com'
    MAIL_PORT           = 587
    MAIL_USE_TLS        = True
    MAIL_USE_SSL        = False
    MAIL_USERNAME       = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD       = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_USERNAME')
    
    # ── Secure Admin Credentials ─────────────────────────────
    ADMIN_EMAIL         = os.environ.get('ADMIN_EMAIL', '')
    ADMIN_USERNAME      = os.environ.get('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD      = os.environ.get('ADMIN_PASSWORD', 'change-me-immediately')

    # ── Security ─────────────────────────────────────────────
    WTF_CSRF_ENABLED         = True
    SESSION_COOKIE_SECURE    = os.environ.get('FLASK_ENV') == 'production'
    SESSION_COOKIE_HTTPONLY  = True
    SESSION_COOKIE_SAMESITE  = 'Lax'

    # ── Owner meta (non-secret, used in templates) ───────────
    OWNER_NAME  = "Deepmani Mishraa"
    OWNER_TITLE = "IIT Madras | Co-Founder @ PRAMANIIK"

    # ── Profile image (set in Render env or .env) ────────────
    PROFILE_IMAGE_URL = os.environ.get('PROFILE_IMAGE_URL', '')