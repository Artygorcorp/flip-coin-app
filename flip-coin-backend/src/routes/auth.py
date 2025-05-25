from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
import hashlib
import hmac
import time
import json
from src.models.models import db, User, UserRole

auth_bp = Blueprint('auth', __name__)

# Secret key for validating Telegram data
BOT_TOKEN = "YOUR_BOT_TOKEN"  # Replace with your actual bot token in production

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

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate user with Telegram Login Widget data
    """
    data = request.json
    
    # For development, skip validation if in debug mode
    # In production, always validate
    if not validate_telegram_data(data) and not request.args.get('debug'):
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

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """
    Get current user profile
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    return jsonify({
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

@auth_bp.route('/profile', methods=['PATCH'])
@jwt_required()
def update_profile():
    """
    Update user profile
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    data = request.json
    
    # Update allowed fields
    if 'nickname' in data:
        user.nickname = data['nickname']
    if 'language' in data and data['language'] in ['en', 'ru']:
        user.language = data['language']
    if 'sound_enabled' in data:
        user.sound_enabled = bool(data['sound_enabled'])
    
    db.session.commit()
    
    return jsonify({
        "message": "Profile updated successfully",
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

@auth_bp.route('/referral', methods=['POST'])
@jwt_required()
def create_referral():
    """
    Process referral code
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    data = request.json
    referrer_code = data.get('referral_code')
    
    if not referrer_code:
        return jsonify({"error": "Referral code is required"}), 400
    
    # Find referrer by telegram_id or nickname
    referrer = User.query.filter(
        (User.telegram_id == referrer_code) | (User.nickname == referrer_code)
    ).first()
    
    if not referrer:
        return jsonify({"error": "Invalid referral code"}), 404
    
    if referrer.id == user.id:
        return jsonify({"error": "You cannot refer yourself"}), 400
    
    # Check if already referred
    existing_referral = Referral.query.filter_by(
        referrer_id=referrer.id,
        referred_id=user.id
    ).first()
    
    if existing_referral:
        return jsonify({"error": "You are already referred by this user"}), 400
    
    # Create referral
    from src.models.models import Referral
    referral = Referral(
        referrer_id=referrer.id,
        referred_id=user.id
    )
    db.session.add(referral)
    
    # Add tokens to both users
    referrer.flip_tokens += 50  # Bonus for referrer
    user.flip_tokens += 20      # Bonus for new user
    referral.reward_given = True
    
    db.session.commit()
    
    return jsonify({
        "message": "Referral processed successfully",
        "tokens_earned": 20,
        "current_balance": user.flip_tokens
    })
