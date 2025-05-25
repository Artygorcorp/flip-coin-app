from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.models import db, User, GameHistory, GameType, DailyLimit
from datetime import datetime, date
import random

games_bp = Blueprint('games', __name__)

# Maximum daily plays per game type
MAX_DAILY_PLAYS = {
    GameType.FLIP_COIN: 50,
    GameType.MAGIC_BALL: 30,
    GameType.TAROT_CARD: 20
}

# Tokens earned per game
TOKENS_PER_GAME = {
    GameType.FLIP_COIN: 1,
    GameType.MAGIC_BALL: 2,
    GameType.TAROT_CARD: 3
}

def check_daily_limit(user_id, game_type):
    """Check if user has reached daily limit for this game type"""
    today = date.today()
    
    # Get or create daily limit record
    daily_limit = DailyLimit.query.filter_by(
        user_id=user_id,
        game_type=game_type,
        date=today
    ).first()
    
    if not daily_limit:
        daily_limit = DailyLimit(
            user_id=user_id,
            game_type=game_type,
            count=0,
            date=today
        )
        db.session.add(daily_limit)
        db.session.commit()
    
    # Check if limit reached
    max_plays = MAX_DAILY_PLAYS.get(game_type, 50)
    return daily_limit.count >= max_plays, daily_limit

def increment_play_count(daily_limit):
    """Increment play count for daily limit"""
    daily_limit.count += 1
    db.session.commit()

def award_tokens(user_id, game_type):
    """Award tokens to user for playing a game"""
    user = User.query.get(user_id)
    tokens = TOKENS_PER_GAME.get(game_type, 1)
    user.flip_tokens += tokens
    db.session.commit()
    return tokens

@games_bp.route('/history', methods=['GET'])
@jwt_required()
def get_game_history():
    """Get user's game history"""
    user_id = get_jwt_identity()
    
    # Get query parameters
    game_type = request.args.get('game_type')
    limit = request.args.get('limit', 10, type=int)
    
    # Build query
    query = GameHistory.query.filter_by(user_id=user_id)
    
    if game_type:
        try:
            game_type_enum = GameType(game_type)
            query = query.filter_by(game_type=game_type_enum)
        except ValueError:
            return jsonify({"error": "Invalid game type"}), 400
    
    # Get results
    history = query.order_by(GameHistory.played_at.desc()).limit(limit).all()
    
    return jsonify({
        "history": [
            {
                "id": h.id,
                "game_type": h.game_type.value,
                "result": h.result,
                "tokens_earned": h.tokens_earned,
                "played_at": h.played_at.isoformat()
            } for h in history
        ]
    })

@games_bp.route('/flip-coin', methods=['POST'])
@jwt_required()
def flip_coin():
    """Play flip coin game"""
    user_id = get_jwt_identity()
    
    # Check daily limit
    limit_reached, daily_limit = check_daily_limit(user_id, GameType.FLIP_COIN)
    
    if limit_reached:
        return jsonify({
            "error": "Daily limit reached",
            "max_plays": MAX_DAILY_PLAYS[GameType.FLIP_COIN],
            "plays_today": daily_limit.count
        }), 429
    
    # Determine result
    result = "heads" if random.random() > 0.5 else "tails"
    
    # Award tokens
    tokens = award_tokens(user_id, GameType.FLIP_COIN)
    
    # Record game history
    game_history = GameHistory(
        user_id=user_id,
        game_type=GameType.FLIP_COIN,
        result=result,
        tokens_earned=tokens
    )
    db.session.add(game_history)
    
    # Increment play count
    increment_play_count(daily_limit)
    
    db.session.commit()
    
    # Get updated user
    user = User.query.get(user_id)
    
    return jsonify({
        "result": result,
        "tokens_earned": tokens,
        "current_balance": user.flip_tokens,
        "plays_today": daily_limit.count,
        "max_plays": MAX_DAILY_PLAYS[GameType.FLIP_COIN]
    })

@games_bp.route('/magic-ball', methods=['POST'])
@jwt_required()
def magic_ball():
    """Play magic 8 ball game"""
    user_id = get_jwt_identity()
    data = request.json
    question = data.get('question', '')
    
    if not question.strip():
        return jsonify({"error": "Question is required"}), 400
    
    # Check daily limit
    limit_reached, daily_limit = check_daily_limit(user_id, GameType.MAGIC_BALL)
    
    if limit_reached:
        return jsonify({
            "error": "Daily limit reached",
            "max_plays": MAX_DAILY_PLAYS[GameType.MAGIC_BALL],
            "plays_today": daily_limit.count
        }), 429
    
    # Get user language
    user = User.query.get(user_id)
    language = user.language
    
    # Possible answers based on language
    answers = {
        'en': [
            "Definitely yes", "Very likely", "Perhaps", "Ask again later",
            "Cannot predict now", "Don't count on it", "My sources say no", "Definitely no"
        ],
        'ru': [
            "Определенно да", "Весьма вероятно", "Возможно", "Спросите позже",
            "Не могу предсказать сейчас", "Не рассчитывайте на это", 
            "Мои источники говорят нет", "Определенно нет"
        ]
    }
    
    # Determine result
    result = random.choice(answers.get(language, answers['en']))
    
    # Award tokens
    tokens = award_tokens(user_id, GameType.MAGIC_BALL)
    
    # Record game history
    game_history = GameHistory(
        user_id=user_id,
        game_type=GameType.MAGIC_BALL,
        result=result,
        tokens_earned=tokens
    )
    db.session.add(game_history)
    
    # Increment play count
    increment_play_count(daily_limit)
    
    db.session.commit()
    
    return jsonify({
        "question": question,
        "result": result,
        "tokens_earned": tokens,
        "current_balance": user.flip_tokens,
        "plays_today": daily_limit.count,
        "max_plays": MAX_DAILY_PLAYS[GameType.MAGIC_BALL]
    })

@games_bp.route('/tarot-card', methods=['POST'])
@jwt_required()
def tarot_card():
    """Play tarot card game"""
    user_id = get_jwt_identity()
    
    # Check daily limit
    limit_reached, daily_limit = check_daily_limit(user_id, GameType.TAROT_CARD)
    
    if limit_reached:
        return jsonify({
            "error": "Daily limit reached",
            "max_plays": MAX_DAILY_PLAYS[GameType.TAROT_CARD],
            "plays_today": daily_limit.count
        }), 429
    
    # Get user language
    user = User.query.get(user_id)
    language = user.language
    
    # Tarot cards
    tarot_cards = [
        {
            "id": 1,
            "name": {"en": "The Fool", "ru": "Шут"},
            "meaning": {
                "en": "New beginnings, spontaneity, freedom, risk, potential",
                "ru": "Новые начинания, спонтанность, свобода, риск, потенциал"
            }
        },
        {
            "id": 2,
            "name": {"en": "The Magician", "ru": "Маг"},
            "meaning": {
                "en": "Manifestation, willpower, skill, inspiration",
                "ru": "Проявление, сила воли, мастерство, вдохновение"
            }
        },
        {
            "id": 3,
            "name": {"en": "The High Priestess", "ru": "Верховная Жрица"},
            "meaning": {
                "en": "Intuition, unconscious, divine feminine",
                "ru": "Интуиция, подсознание, божественное женское начало"
            }
        },
        {
            "id": 4,
            "name": {"en": "The Empress", "ru": "Императрица"},
            "meaning": {
                "en": "Fertility, femininity, beauty, nature, abundance",
                "ru": "Плодородие, женственность, красота, природа, изобилие"
            }
        },
        {
            "id": 5,
            "name": {"en": "The Emperor", "ru": "Император"},
            "meaning": {
                "en": "Authority, structure, control, fatherhood",
                "ru": "Авторитет, структура, контроль, отцовская фигура"
            }
        },
        {
            "id": 6,
            "name": {"en": "The Hierophant", "ru": "Иерофант"},
            "meaning": {
                "en": "Spiritual wisdom, religious beliefs, tradition",
                "ru": "Духовная мудрость, религиозные убеждения, традиции"
            }
        },
        {
            "id": 7,
            "name": {"en": "The Lovers", "ru": "Влюбленные"},
            "meaning": {
                "en": "Love, harmony, relationships, choices, alignment of values",
                "ru": "Любовь, гармония, отношения, выбор, выравнивание ценностей"
            }
        },
        {
            "id": 8,
            "name": {"en": "The Chariot", "ru": "Колесница"},
            "meaning": {
                "en": "Control, willpower, victory, assertion, determination",
                "ru": "Контроль, сила воли, победа, напор, решительность"
            }
        }
    ]
    
    # Determine result
    card = random.choice(tarot_cards)
    result = f"{card['name'][language]}: {card['meaning'][language]}"
    
    # Award tokens
    tokens = award_tokens(user_id, GameType.TAROT_CARD)
    
    # Record game history
    game_history = GameHistory(
        user_id=user_id,
        game_type=GameType.TAROT_CARD,
        result=result,
        tokens_earned=tokens
    )
    db.session.add(game_history)
    
    # Increment play count
    increment_play_count(daily_limit)
    
    db.session.commit()
    
    return jsonify({
        "card": {
            "id": card["id"],
            "name": card["name"][language],
            "meaning": card["meaning"][language]
        },
        "tokens_earned": tokens,
        "current_balance": user.flip_tokens,
        "plays_today": daily_limit.count,
        "max_plays": MAX_DAILY_PLAYS[GameType.TAROT_CARD]
    })

@games_bp.route('/limits', methods=['GET'])
@jwt_required()
def get_limits():
    """Get user's daily game limits"""
    user_id = get_jwt_identity()
    today = date.today()
    
    # Get all daily limits for today
    limits = DailyLimit.query.filter_by(
        user_id=user_id,
        date=today
    ).all()
    
    # Convert to dict for easier lookup
    limits_dict = {limit.game_type: limit.count for limit in limits}
    
    return jsonify({
        "limits": {
            "flip_coin": {
                "current": limits_dict.get(GameType.FLIP_COIN, 0),
                "max": MAX_DAILY_PLAYS[GameType.FLIP_COIN]
            },
            "magic_ball": {
                "current": limits_dict.get(GameType.MAGIC_BALL, 0),
                "max": MAX_DAILY_PLAYS[GameType.MAGIC_BALL]
            },
            "tarot_card": {
                "current": limits_dict.get(GameType.TAROT_CARD, 0),
                "max": MAX_DAILY_PLAYS[GameType.TAROT_CARD]
            }
        }
    })
