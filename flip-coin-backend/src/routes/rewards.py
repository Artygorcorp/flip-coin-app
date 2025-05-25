from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.models import db, User, Reward, RedeemedReward, UserRole
from datetime import datetime

rewards_bp = Blueprint('rewards', __name__)

def check_admin_or_tester(user_id):
    """Check if user is admin or tester"""
    user = User.query.get(user_id)
    return user and user.role in [UserRole.ADMIN, UserRole.TESTER]

@rewards_bp.route('/', methods=['GET'])
@jwt_required()
def get_rewards():
    """Get all available rewards"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Get all active rewards
    rewards = Reward.query.filter_by(is_active=True).all()
    
    result = []
    for reward in rewards:
        # Skip if out of stock
        if reward.stock is not None and reward.stock <= 0:
            continue
        
        result.append({
            "id": reward.id,
            "name": reward.name_en if user.language == 'en' else reward.name_ru,
            "description": reward.description_en if user.language == 'en' else reward.description_ru,
            "image": reward.image,
            "cost": reward.cost,
            "can_afford": user.flip_tokens >= reward.cost
        })
    
    return jsonify({
        "rewards": result,
        "user_balance": user.flip_tokens
    })

@rewards_bp.route('/<int:reward_id>/redeem', methods=['POST'])
@jwt_required()
def redeem_reward(reward_id):
    """Redeem a reward"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Get reward
    reward = Reward.query.get(reward_id)
    
    if not reward:
        return jsonify({"error": "Reward not found"}), 404
    
    if not reward.is_active:
        return jsonify({"error": "Reward is not available"}), 400
    
    # Check if out of stock
    if reward.stock is not None and reward.stock <= 0:
        return jsonify({"error": "Reward is out of stock"}), 400
    
    # Check if user can afford
    if user.flip_tokens < reward.cost:
        return jsonify({
            "error": "Insufficient tokens",
            "required": reward.cost,
            "balance": user.flip_tokens
        }), 400
    
    # Redeem reward
    redeemed = RedeemedReward(
        user_id=user_id,
        reward_id=reward_id,
        tokens_spent=reward.cost
    )
    db.session.add(redeemed)
    
    # Deduct tokens
    user.flip_tokens -= reward.cost
    
    # Update stock if applicable
    if reward.stock is not None:
        reward.stock -= 1
    
    db.session.commit()
    
    return jsonify({
        "message": "Reward redeemed successfully",
        "tokens_spent": reward.cost,
        "current_balance": user.flip_tokens
    })

@rewards_bp.route('/history', methods=['GET'])
@jwt_required()
def get_reward_history():
    """Get user's reward redemption history"""
    user_id = get_jwt_identity()
    
    # Get query parameters
    limit = request.args.get('limit', 10, type=int)
    
    # Get redeemed rewards
    redeemed = RedeemedReward.query.filter_by(user_id=user_id).order_by(
        RedeemedReward.redeemed_at.desc()
    ).limit(limit).all()
    
    # Get reward details
    result = []
    for r in redeemed:
        reward = Reward.query.get(r.reward_id)
        if reward:
            result.append({
                "id": r.id,
                "reward_id": reward.id,
                "name_en": reward.name_en,
                "name_ru": reward.name_ru,
                "tokens_spent": r.tokens_spent,
                "redeemed_at": r.redeemed_at.isoformat()
            })
    
    return jsonify({"redeemed_rewards": result})

# Admin routes for reward management
@rewards_bp.route('/admin', methods=['POST'])
@jwt_required()
def create_reward():
    """Create a new reward (admin only)"""
    user_id = get_jwt_identity()
    
    if not check_admin_or_tester(user_id):
        return jsonify({"error": "Unauthorized"}), 403
    
    data = request.json
    
    # Validate required fields
    required_fields = ['name_en', 'name_ru', 'description_en', 'description_ru', 'cost']
    
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    # Create reward
    reward = Reward(
        name_en=data['name_en'],
        name_ru=data['name_ru'],
        description_en=data['description_en'],
        description_ru=data['description_ru'],
        image=data.get('image'),
        cost=data['cost'],
        is_active=data.get('is_active', True),
        stock=data.get('stock')
    )
    
    db.session.add(reward)
    db.session.commit()
    
    return jsonify({
        "message": "Reward created successfully",
        "reward": {
            "id": reward.id,
            "name_en": reward.name_en,
            "name_ru": reward.name_ru,
            "cost": reward.cost
        }
    }), 201

@rewards_bp.route('/admin/<int:reward_id>', methods=['PUT'])
@jwt_required()
def update_reward(reward_id):
    """Update a reward (admin only)"""
    user_id = get_jwt_identity()
    
    if not check_admin_or_tester(user_id):
        return jsonify({"error": "Unauthorized"}), 403
    
    reward = Reward.query.get(reward_id)
    
    if not reward:
        return jsonify({"error": "Reward not found"}), 404
    
    data = request.json
    
    # Update fields
    if 'name_en' in data:
        reward.name_en = data['name_en']
    if 'name_ru' in data:
        reward.name_ru = data['name_ru']
    if 'description_en' in data:
        reward.description_en = data['description_en']
    if 'description_ru' in data:
        reward.description_ru = data['description_ru']
    if 'image' in data:
        reward.image = data['image']
    if 'cost' in data:
        reward.cost = data['cost']
    if 'is_active' in data:
        reward.is_active = data['is_active']
    if 'stock' in data:
        reward.stock = data['stock']
    
    db.session.commit()
    
    return jsonify({
        "message": "Reward updated successfully",
        "reward": {
            "id": reward.id,
            "name_en": reward.name_en,
            "name_ru": reward.name_ru,
            "cost": reward.cost,
            "is_active": reward.is_active,
            "stock": reward.stock
        }
    })

@rewards_bp.route('/admin/<int:reward_id>', methods=['DELETE'])
@jwt_required()
def delete_reward(reward_id):
    """Delete a reward (admin only)"""
    user_id = get_jwt_identity()
    
    if not check_admin_or_tester(user_id):
        return jsonify({"error": "Unauthorized"}), 403
    
    reward = Reward.query.get(reward_id)
    
    if not reward:
        return jsonify({"error": "Reward not found"}), 404
    
    db.session.delete(reward)
    db.session.commit()
    
    return jsonify({"message": "Reward deleted successfully"})
