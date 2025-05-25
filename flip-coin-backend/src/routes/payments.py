from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.models import db, User, Payment, PaymentStatus, UserRole
from datetime import datetime
import hashlib
import hmac
import json

payments_bp = Blueprint('payments', __name__)

# Secret key for validating Telegram data
BOT_TOKEN = "YOUR_BOT_TOKEN"  # Replace with your actual bot token in production

def check_admin(user_id):
    """Check if user is admin"""
    user = User.query.get(user_id)
    return user and user.role == UserRole.ADMIN

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

@payments_bp.route('/packages', methods=['GET'])
@jwt_required()
def get_token_packages():
    """Get available token packages for purchase"""
    # These could be stored in the database, but for simplicity we'll hardcode them
    packages = [
        {
            "id": "small",
            "tokens": 100,
            "price": 1.99,
            "currency": "USD",
            "description": {
                "en": "100 FLIP tokens",
                "ru": "100 FLIP токенов"
            }
        },
        {
            "id": "medium",
            "tokens": 300,
            "price": 4.99,
            "currency": "USD",
            "description": {
                "en": "300 FLIP tokens",
                "ru": "300 FLIP токенов"
            }
        },
        {
            "id": "large",
            "tokens": 500,
            "price": 7.99,
            "currency": "USD",
            "description": {
                "en": "500 FLIP tokens",
                "ru": "500 FLIP токенов"
            }
        },
        {
            "id": "premium",
            "tokens": 1000,
            "price": 14.99,
            "currency": "USD",
            "description": {
                "en": "1000 FLIP tokens",
                "ru": "1000 FLIP токенов"
            }
        }
    ]
    
    return jsonify({"packages": packages})

@payments_bp.route('/create', methods=['POST'])
@jwt_required()
def create_payment():
    """Create a payment for tokens"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    data = request.json
    package_id = data.get('package_id')
    
    # Get package details
    packages = {
        "small": {"tokens": 100, "price": 1.99},
        "medium": {"tokens": 300, "price": 4.99},
        "large": {"tokens": 500, "price": 7.99},
        "premium": {"tokens": 1000, "price": 14.99}
    }
    
    if package_id not in packages:
        return jsonify({"error": "Invalid package ID"}), 400
    
    package = packages[package_id]
    
    # Create payment record
    payment = Payment(
        user_id=user_id,
        amount=package["price"],
        tokens_amount=package["tokens"],
        status=PaymentStatus.PENDING
    )
    
    db.session.add(payment)
    db.session.commit()
    
    # In a real implementation, you would integrate with Telegram Payments API here
    # For now, we'll just return the payment ID that would be used in the callback
    
    return jsonify({
        "payment_id": payment.id,
        "amount": payment.amount,
        "tokens": payment.tokens_amount,
        "status": payment.status.value,
        "telegram_payment_url": f"https://t.me/your_bot?start=payment_{payment.id}"
    })

@payments_bp.route('/webhook', methods=['POST'])
def payment_webhook():
    """Webhook for Telegram Payments"""
    data = request.json
    
    # Validate payment data from Telegram
    if not validate_telegram_payment(data):
        return jsonify({"error": "Invalid payment data"}), 401
    
    # Extract payment details
    telegram_payment_id = data.get('telegram_payment_id')
    payment_id = data.get('payment_id')  # This would be passed in the start parameter
    status = data.get('status')
    
    if not payment_id:
        return jsonify({"error": "Payment ID not provided"}), 400
    
    # Find payment
    payment = Payment.query.get(payment_id)
    
    if not payment:
        return jsonify({"error": "Payment not found"}), 404
    
    # Update payment status
    if status == 'successful':
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

@payments_bp.route('/history', methods=['GET'])
@jwt_required()
def get_payment_history():
    """Get user's payment history"""
    user_id = get_jwt_identity()
    
    # Get query parameters
    limit = request.args.get('limit', 10, type=int)
    
    # Get payments
    payments = Payment.query.filter_by(user_id=user_id).order_by(
        Payment.created_at.desc()
    ).limit(limit).all()
    
    result = []
    for p in payments:
        result.append({
            "id": p.id,
            "amount": p.amount,
            "tokens_amount": p.tokens_amount,
            "status": p.status.value,
            "created_at": p.created_at.isoformat(),
            "completed_at": p.completed_at.isoformat() if p.completed_at else None
        })
    
    return jsonify({"payments": result})

# Admin routes
@payments_bp.route('/admin/payments', methods=['GET'])
@jwt_required()
def admin_get_payments():
    """Get all payments (admin only)"""
    user_id = get_jwt_identity()
    
    if not check_admin(user_id):
        return jsonify({"error": "Unauthorized"}), 403
    
    # Get query parameters
    limit = request.args.get('limit', 50, type=int)
    status = request.args.get('status')
    
    # Build query
    query = Payment.query
    
    if status:
        try:
            status_enum = PaymentStatus(status)
            query = query.filter_by(status=status_enum)
        except ValueError:
            return jsonify({"error": "Invalid status"}), 400
    
    # Get payments
    payments = query.order_by(Payment.created_at.desc()).limit(limit).all()
    
    result = []
    for p in payments:
        user = User.query.get(p.user_id)
        result.append({
            "id": p.id,
            "user_id": p.user_id,
            "user_nickname": user.nickname if user else "Unknown",
            "amount": p.amount,
            "tokens_amount": p.tokens_amount,
            "status": p.status.value,
            "created_at": p.created_at.isoformat(),
            "completed_at": p.completed_at.isoformat() if p.completed_at else None
        })
    
    return jsonify({"payments": result})

@payments_bp.route('/admin/payments/<int:payment_id>', methods=['PUT'])
@jwt_required()
def admin_update_payment(payment_id):
    """Update payment status (admin only)"""
    user_id = get_jwt_identity()
    
    if not check_admin(user_id):
        return jsonify({"error": "Unauthorized"}), 403
    
    payment = Payment.query.get(payment_id)
    
    if not payment:
        return jsonify({"error": "Payment not found"}), 404
    
    data = request.json
    status = data.get('status')
    
    if not status:
        return jsonify({"error": "Status is required"}), 400
    
    try:
        status_enum = PaymentStatus(status)
    except ValueError:
        return jsonify({"error": "Invalid status"}), 400
    
    # Update payment
    old_status = payment.status
    payment.status = status_enum
    
    # If completing a pending payment, add tokens
    if old_status == PaymentStatus.PENDING and status_enum == PaymentStatus.COMPLETED:
        payment.completed_at = datetime.utcnow()
        
        # Add tokens to user
        user = User.query.get(payment.user_id)
        if user:
            user.flip_tokens += payment.tokens_amount
    
    db.session.commit()
    
    return jsonify({
        "message": "Payment updated successfully",
        "payment": {
            "id": payment.id,
            "status": payment.status.value,
            "completed_at": payment.completed_at.isoformat() if payment.completed_at else None
        }
    })
