import os
import requests
from flask import Blueprint, request, jsonify, redirect, url_for
from flask_jwt_extended import create_access_token
import hashlib
import hmac
import time
from src.models.models import db, User, UserRole

# Create blueprint for Telegram integration
telegram_bp = Blueprint('telegram', __name__)

# Telegram Bot API configuration
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', 'YOUR_BOT_TOKEN')
BOT_USERNAME = os.getenv('TELEGRAM_BOT_USERNAME', 'your_bot_username')

# Telegram Login Widget configuration
LOGIN_URL = f"https://oauth.telegram.org/auth?bot_id={BOT_USERNAME}"

@telegram_bp.route('/login', methods=['GET'])
def login_with_telegram():
    """
    Redirect to Telegram Login Widget
    """
    # Generate redirect URL for after authentication
    redirect_url = request.args.get('redirect_url', '/')
    
    # Store redirect URL in session or use a state parameter
    
    return redirect(LOGIN_URL)

@telegram_bp.route('/callback', methods=['POST'])
def telegram_callback():
    """
    Handle callback from Telegram Login Widget
    """
    data = request.json
    
    # Validate the data
    if not validate_telegram_data(data):
        return jsonify({"error": "Invalid authentication data"}), 401
    
    telegram_id = data.get('id')
    if not telegram_id:
        return jsonify({"error": "Telegram ID is required"}), 400
    
    # Check if user exists
    user = User.query.filter_by(telegram_id=telegram_id).first()
    
    if not user:
        # Create new user
        user = User(
            telegram_id=telegram_id,
            username=data.get('username'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            nickname=data.get('username') or f"user_{telegram_id}",
            language=data.get('language_code', 'en')[:2]
        )
        db.session.add(user)
        db.session.commit()
    else:
        # Update user data
        user.username = data.get('username', user.username)
        user.first_name = data.get('first_name', user.first_name)
        user.last_name = data.get('last_name', user.last_name)
        user.language = data.get('language_code', user.language)[:2]
        db.session.commit()
    
    # Create access token
    access_token = create_access_token(identity=user.id)
    
    return jsonify({
        "access_token": access_token,
        "user": {
            "id": user.id,
            "telegram_id": user.telegram_id,
            "nickname": user.nickname,
            "flip_tokens": user.flip_tokens,
            "language": user.language,
            "sound_enabled": user.sound_enabled,
            "role": user.role.value
        }
    })

def validate_telegram_data(data):
    """
    Validate the data received from Telegram Login Widget
    """
    if 'hash' not in data:
        return False
    
    auth_data = {k: v for k, v in data.items() if k != 'hash'}
    data_check_string = '\n'.join([f"{k}={v}" for k, v in sorted(auth_data.items())])
    
    secret_key = hashlib.sha256(BOT_TOKEN.encode()).digest()
    hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    
    return hash == data['hash'] and time.time() - int(data['auth_date']) < 86400

@telegram_bp.route('/payments/init', methods=['POST'])
def init_payment():
    """
    Initialize a payment with Telegram Payments
    """
    data = request.json
    
    # Extract payment details
    amount = data.get('amount')
    description = data.get('description')
    payload = data.get('payload')  # Custom data to identify the payment
    
    if not all([amount, description, payload]):
        return jsonify({"error": "Missing required fields"}), 400
    
    # In a real implementation, you would call the Telegram Bot API to create an invoice
    # For example:
    # url = f"https://api.telegram.org/bot{BOT_TOKEN}/createInvoice"
    # payload = {
    #     "title": "FLIP Tokens",
    #     "description": description,
    #     "payload": payload,
    #     "provider_token": "PAYMENT_PROVIDER_TOKEN",
    #     "currency": "USD",
    #     "prices": [{"label": "FLIP Tokens", "amount": int(amount * 100)}]  # Amount in cents
    # }
    # response = requests.post(url, json=payload)
    # result = response.json()
    
    # For now, we'll just return a mock response
    return jsonify({
        "success": True,
        "payment_url": f"https://t.me/{BOT_USERNAME}?start=pay_{payload}"
    })

@telegram_bp.route('/payments/callback', methods=['POST'])
def payment_callback():
    """
    Handle callback from Telegram Payments
    """
    data = request.json
    
    # Validate the payment data
    if not validate_telegram_payment(data):
        return jsonify({"error": "Invalid payment data"}), 401
    
    # Extract payment details
    telegram_payment_id = data.get('telegram_payment_id')
    payload = data.get('payload')  # This should contain our payment ID
    status = data.get('status')
    
    # Process the payment in our database
    from src.models.models import Payment, PaymentStatus
    
    # Extract our payment ID from the payload
    try:
        payment_id = int(payload.split('_')[1])
    except (ValueError, IndexError):
        return jsonify({"error": "Invalid payload format"}), 400
    
    # Find payment
    payment = Payment.query.get(payment_id)
    
    if not payment:
        return jsonify({"error": "Payment not found"}), 404
    
    # Update payment status
    if status == 'paid':
        payment.status = PaymentStatus.COMPLETED
        payment.telegram_payment_id = telegram_payment_id
        payment.completed_at = datetime.utcnow()
        
        # Add tokens to user
        user = User.query.get(payment.user_id)
        user.flip_tokens += payment.tokens_amount
        
        db.session.commit()
        
        return jsonify({"success": True, "message": "Payment processed successfully"})
    
    elif status == 'failed':
        payment.status = PaymentStatus.FAILED
        db.session.commit()
        
        return jsonify({"success": True, "message": "Payment marked as failed"})
    
    else:
        return jsonify({"error": "Invalid payment status"}), 400

def validate_telegram_payment(payment_data):
    """
    Validate the payment data received from Telegram Payments
    """
    if 'hash' not in payment_data:
        return False
    
    data_check_arr = []
    for k, v in sorted(payment_data.items()):
        if k != 'hash':
            data_check_arr.append(f"{k}={v}")
    
    data_check_string = '\n'.join(data_check_arr)
    
    secret_key = hashlib.sha256(BOT_TOKEN.encode()).digest()
    hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    
    return hash == payment_data['hash']
