"""
config.py — All configuration loaded from environment variables.
Never hardcode secrets here. Use .env for local dev (see .env.example).
"""
import os
from dotenv import load_dotenv

load_dotenv() 

class Config:
    # ── Core ────────────────────────────────────────────────
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'change-this-before-deploying'

    # ── Database ─────────────────────────────────────────────
    _db_url = os.environ.get('DATABASE_URL', 'sqlite:///dev.db')
    if _db_url.startswith('postgres://'):
        _db_url = _db_url.replace('postgres://', 'postgresql://', 1)
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
    ADMIN_EMAIL         = os.environ.get('ADMIN_EMAIL', '')

    # ── Admin Seed Credentials ───────────────────────────────
    # Strictly pulling from .env. No hardcoded fallback strings allowed.
    SEED_ADMIN_USERNAME = os.environ.get('SEED_ADMIN_USERNAME')
    SEED_ADMIN_EMAIL    = os.environ.get('SEED_ADMIN_EMAIL')
    SEED_ADMIN_PASSWORD = os.environ.get('SEED_ADMIN_PASSWORD')

    # ── Security ─────────────────────────────────────────────
    WTF_CSRF_ENABLED         = True
    SESSION_COOKIE_SECURE    = os.environ.get('FLASK_ENV') == 'production'
    SESSION_COOKIE_HTTPONLY  = True
    SESSION_COOKIE_SAMESITE  = 'Lax'

    # ── Owner meta (non-secret, used in templates) ───────────
    OWNER_NAME  = "Deepmani Mishraa"
    OWNER_TITLE = "Student | IIT Madras  .  Co-founder | Pramaniik"

    # ── Profile image (set in Render env or .env) ────────────
    PROFILE_IMAGE_URL = os.environ.get('PROFILE_IMAGE_URL', '')