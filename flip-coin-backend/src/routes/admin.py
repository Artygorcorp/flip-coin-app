from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.models import db, User, UserRole
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

def check_admin(user_id):
    """Check if user is admin"""
    user = User.query.get(user_id)
    return user and user.role == UserRole.ADMIN

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    """Get all users (admin only)"""
    user_id = get_jwt_identity()
    
    if not check_admin(user_id):
        return jsonify({"error": "Unauthorized"}), 403
    
    # Get query parameters
    limit = request.args.get('limit', 50, type=int)
    role = request.args.get('role')
    
    # Build query
    query = User.query
    
    if role:
        try:
            role_enum = UserRole(role)
            query = query.filter_by(role=role_enum)
        except ValueError:
            return jsonify({"error": "Invalid role"}), 400
    
    # Get users
    users = query.order_by(User.created_at.desc()).limit(limit).all()
    
    result = []
    for user in users:
        result.append({
            "id": user.id,
            "telegram_id": user.telegram_id,
            "username": user.username,
            "nickname": user.nickname,
            "flip_tokens": user.flip_tokens,
            "language": user.language,
            "role": user.role.value,
            "created_at": user.created_at.isoformat(),
            "last_login": user.last_login.isoformat()
        })
    
    return jsonify({"users": result})

@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
def update_user(user_id):
    """Update user (admin only)"""
    admin_id = get_jwt_identity()
    
    if not check_admin(admin_id):
        return jsonify({"error": "Unauthorized"}), 403
    
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    data = request.json
    
    # Update fields
    if 'nickname' in data:
        user.nickname = data['nickname']
    if 'flip_tokens' in data:
        user.flip_tokens = data['flip_tokens']
    if 'language' in data and data['language'] in ['en', 'ru']:
        user.language = data['language']
    if 'sound_enabled' in data:
        user.sound_enabled = bool(data['sound_enabled'])
    
    # Update role if provided
    if 'role' in data:
        try:
            user.role = UserRole(data['role'])
        except ValueError:
            return jsonify({"error": "Invalid role"}), 400
    
    db.session.commit()
    
    return jsonify({
        "message": "User updated successfully",
        "user": {
            "id": user.id,
            "telegram_id": user.telegram_id,
            "nickname": user.nickname,
            "flip_tokens": user.flip_tokens,
            "language": user.language,
            "role": user.role.value
        }
    })

@admin_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """Get system statistics (admin only)"""
    user_id = get_jwt_identity()
    
    if not check_admin(user_id):
        return jsonify({"error": "Unauthorized"}), 403
    
    # Get basic stats
    total_users = User.query.count()
    
    # Users by role
    admin_count = User.query.filter_by(role=UserRole.ADMIN).count()
    tester_count = User.query.filter_by(role=UserRole.TESTER).count()
    user_count = User.query.filter_by(role=UserRole.USER).count()
    
    # Get game stats
    from src.models.models import GameHistory, GameType
    
    total_games = GameHistory.query.count()
    
    # Games by type
    flip_coin_count = GameHistory.query.filter_by(game_type=GameType.FLIP_COIN).count()
    magic_ball_count = GameHistory.query.filter_by(game_type=GameType.MAGIC_BALL).count()
    tarot_card_count = GameHistory.query.filter_by(game_type=GameType.TAROT_CARD).count()
    
    # Get task stats
    from src.models.models import Task, CompletedTask
    
    total_tasks = Task.query.count()
    completed_tasks = CompletedTask.query.count()
    
    # Get reward stats
    from src.models.models import Reward, RedeemedReward
    
    total_rewards = Reward.query.count()
    redeemed_rewards = RedeemedReward.query.count()
    
    # Get payment stats
    from src.models.models import Payment, PaymentStatus
    
    total_payments = Payment.query.count()
    completed_payments = Payment.query.filter_by(status=PaymentStatus.COMPLETED).count()
    
    # Calculate total tokens in system
    total_tokens = db.session.query(db.func.sum(User.flip_tokens)).scalar() or 0
    
    return jsonify({
        "users": {
            "total": total_users,
            "by_role": {
                "admin": admin_count,
                "tester": tester_count,
                "user": user_count
            }
        },
        "games": {
            "total": total_games,
            "by_type": {
                "flip_coin": flip_coin_count,
                "magic_ball": magic_ball_count,
                "tarot_card": tarot_card_count
            }
        },
        "tasks": {
            "total": total_tasks,
            "completed": completed_tasks
        },
        "rewards": {
            "total": total_rewards,
            "redeemed": redeemed_rewards
        },
        "payments": {
            "total": total_payments,
            "completed": completed_payments
        },
        "tokens": {
            "total_in_system": total_tokens
        }
    })

@admin_bp.route('/seed', methods=['POST'])
@jwt_required()
def seed_data():
    """Seed initial data (admin only)"""
    user_id = get_jwt_identity()
    
    if not check_admin(user_id):
        return jsonify({"error": "Unauthorized"}), 403
    
    # Seed tasks
    from src.models.models import Task, TaskType, GameType
    
    # Check if tasks already exist
    if Task.query.count() > 0:
        return jsonify({"message": "Data already seeded"}), 400
    
    # Create daily tasks
    daily_tasks = [
        {
            "title_en": "Play Flip Coin 5 times",
            "title_ru": "Сыграть в Орел или Решка 5 раз",
            "description_en": "Flip the coin 5 times in a single day",
            "description_ru": "Подбросить монетку 5 раз за один день",
            "task_type": TaskType.DAILY,
            "reward_tokens": 10,
            "required_game_type": GameType.FLIP_COIN,
            "required_count": 5
        },
        {
            "title_en": "Ask the Magic Ball",
            "title_ru": "Спросить Магический Шар",
            "description_en": "Ask the Magic 8 Ball a question",
            "description_ru": "Задать вопрос Магическому Шару",
            "task_type": TaskType.DAILY,
            "reward_tokens": 15,
            "required_game_type": GameType.MAGIC_BALL,
            "required_count": 1
        },
        {
            "title_en": "Draw a Tarot Card",
            "title_ru": "Вытянуть карту Таро",
            "description_en": "Draw a Tarot Card for daily guidance",
            "description_ru": "Вытянуть карту Таро для ежедневного руководства",
            "task_type": TaskType.DAILY,
            "reward_tokens": 20,
            "required_game_type": GameType.TAROT_CARD,
            "required_count": 1
        }
    ]
    
    # Create weekly tasks
    weekly_tasks = [
        {
            "title_en": "Flip Coin Master",
            "title_ru": "Мастер Монетки",
            "description_en": "Flip the coin 30 times in a week",
            "description_ru": "Подбросить монетку 30 раз за неделю",
            "task_type": TaskType.WEEKLY,
            "reward_tokens": 50,
            "required_game_type": GameType.FLIP_COIN,
            "required_count": 30
        },
        {
            "title_en": "Fortune Teller",
            "title_ru": "Предсказатель",
            "description_en": "Use Magic Ball and Tarot Card 10 times each in a week",
            "description_ru": "Использовать Магический Шар и Карты Таро по 10 раз за неделю",
            "task_type": TaskType.WEEKLY,
            "reward_tokens": 75,
            "required_game_type": None,
            "required_count": 20
        }
    ]
    
    # Create achievement tasks
    achievement_tasks = [
        {
            "title_en": "Coin Flip Addict",
            "title_ru": "Зависимость от Монетки",
            "description_en": "Flip the coin 1000 times",
            "description_ru": "Подбросить монетку 1000 раз",
            "task_type": TaskType.ACHIEVEMENT,
            "reward_tokens": 200,
            "required_game_type": GameType.FLIP_COIN,
            "required_count": 1000
        },
        {
            "title_en": "Mystic Master",
            "title_ru": "Мастер Мистики",
            "description_en": "Use Magic Ball and Tarot Card 500 times combined",
            "description_ru": "Использовать Магический Шар и Карты Таро в сумме 500 раз",
            "task_type": TaskType.ACHIEVEMENT,
            "reward_tokens": 300,
            "required_game_type": None,
            "required_count": 500
        }
    ]
    
    # Add all tasks to database
    for task_data in daily_tasks + weekly_tasks + achievement_tasks:
        task = Task(**task_data)
        db.session.add(task)
    
    # Seed rewards
    from src.models.models import Reward
    
    rewards = [
        {
            "name_en": "Coin Sticker Pack",
            "name_ru": "Стикерпак 'Монетки'",
            "description_en": "10 coin-themed stickers for Telegram",
            "description_ru": "Набор из 10 стикеров с монетками для Telegram",
            "image": "🎭",
            "cost": 50,
            "stock": 100
        },
        {
            "name_en": "VIP Status",
            "name_ru": "VIP статус",
            "description_en": "Special status in the app and access to exclusive games",
            "description_ru": "Особый статус в приложении и доступ к эксклюзивным играм",
            "image": "👑",
            "cost": 100,
            "stock": 50
        },
        {
            "name_en": "Custom Theme",
            "name_ru": "Кастомная тема",
            "description_en": "Unique theme for the application",
            "description_ru": "Уникальная тема оформления для приложения",
            "image": "🎨",
            "cost": 75,
            "stock": 30
        },
        {
            "name_en": "Premium Avatar",
            "name_ru": "Премиум аватар",
            "description_en": "Exclusive avatar for your profile",
            "description_ru": "Эксклюзивный аватар для вашего профиля",
            "image": "🧩",
            "cost": 60,
            "stock": 40
        }
    ]
    
    for reward_data in rewards:
        reward = Reward(**reward_data)
        db.session.add(reward)
    
    db.session.commit()
    
    return jsonify({
        "message": "Data seeded successfully",
        "tasks_created": len(daily_tasks) + len(weekly_tasks) + len(achievement_tasks),
        "rewards_created": len(rewards)
    })
