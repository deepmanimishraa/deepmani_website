from flask import Blueprint, request, jsonify, current_app
from flask_mail import Message as MailMessage
from threading import Thread

# Standardized imports
from core.models import db, Message
from core import mail

messages_bp = Blueprint('messages', __name__)

# ─── BACKGROUND WORKER ──────────────────────────────────────
def send_async_email(app, msg):
    """Sends the email in a background thread so the UI doesn't freeze."""
    with app.app_context():
        try:
            mail.send(msg)
        except Exception as e:
            print(f"\n🔥 GMAIL BACKGROUND ERROR: {str(e)}\n")

# ─── ROUTE ──────────────────────────────────────────────────
@messages_bp.route('/send', methods=['POST'])
def send_message():
    data = request.get_json(silent=True) or {}
    guest_id = request.cookies.get('guest_id', '')

    name    = (data.get('name')    or '').strip()[:100]
    email   = (data.get('email')   or '').strip()[:120]
    subject = (data.get('subject') or '').strip()[:200]
    content = (data.get('message') or '').strip()

    if not name or not email or not content:
        return jsonify({'success': False, 'message': 'Please fill in all required fields.'}), 400

    # 1. Save to PostgreSQL Database instantly
    msg = Message(
        sender_name=name, sender_email=email,
        subject=subject, content=content,
        visitor_id=guest_id or None,
    )
    db.session.add(msg)
    db.session.commit()

    # 2. Prepare the Email Notification
    admin_email = current_app.config.get('ADMIN_EMAIL')
    mail_user = current_app.config.get('MAIL_USERNAME')
    
    if admin_email and mail_user:
        notification = MailMessage(
            subject=f"[deepmani.in] New message from {name}",
            sender=mail_user,
            recipients=[admin_email],
            body=(
                f"From: {name} <{email}>\n"
                f"Subject: {subject}\n\n{content}\n\n"
                f"---\nReply at your admin panel → /admin/messages"
            )
        )
        
        # 3. 🚀 Fire and Forget! Hand it to the background thread
        app = current_app._get_current_object()
        Thread(target=send_async_email, args=(app, notification)).start()

    # 4. Return instant success to the user
    return jsonify({'success': True, 'message': "Message sent! I'll get back to you soon. 🚀"})