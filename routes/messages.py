from flask import Blueprint, request, jsonify, current_app
from email_validator import validate_email, EmailNotValidError

messages_bp = Blueprint('messages', __name__)

@messages_bp.route('/send', methods=['POST'])
def send_message():
    data = request.get_json(silent=True) or {}
    from models import db, Message
    guest_id = request.cookies.get('guest_id', '')

    name      = (data.get('name')    or '').strip()[:100]
    raw_email = (data.get('email')   or '').strip()[:120]
    subject   = (data.get('subject') or '').strip()[:200]
    content   = (data.get('message') or '').strip()

    if not name or not raw_email or not content:
        return jsonify({'success': False, 'message': 'Please fill in all required fields.'}), 400

    # ── THE ZERO-TRUST VALIDATION (DNS BYPASSED FOR CLOUD DEPLOYMENT) ──
    try:
        email_info = validate_email(raw_email, check_deliverability=False)
        clean_email = email_info.normalized 
    except EmailNotValidError as e:
        return jsonify({'success': False, 'message': f"Invalid email: {str(e)}"}), 400

    msg = Message(
        sender_name=name, sender_email=clean_email,
        subject=subject, content=content,
        visitor_id=guest_id or None,
    )
    db.session.add(msg)
    db.session.commit()

    try:
        from app import mail
        from flask_mail import Message as MailMessage
        admin_email = current_app.config.get('ADMIN_EMAIL')
        if admin_email and current_app.config.get('MAIL_USERNAME'):
            notification = MailMessage(
                subject=f"[PRAMANIIK Alert] New message from {name}",
                recipients=[admin_email],
                body=f"From: {name} <{clean_email}>\nSubject: {subject}\n\n{content}\n\n---\nReply at your admin panel."
            )
            mail.send(notification)
    except Exception as e:
        print(f"Mail failed to send: {e}")
        pass

    return jsonify({'success': True, 'message': "Message sent! We'll get back to you soon. 🚀"})