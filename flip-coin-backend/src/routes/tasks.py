from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.models import db, User, Task, CompletedTask, TaskType, GameType, UserRole
from datetime import datetime, timedelta

tasks_bp = Blueprint('tasks', __name__)

def check_admin_or_tester(user_id):
    """Check if user is admin or tester"""
    user = User.query.get(user_id)
    return user and user.role in [UserRole.ADMIN, UserRole.TESTER]

@tasks_bp.route('/', methods=['GET'])
@jwt_required()
def get_tasks():
    """Get all available tasks for the user"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Get all active tasks
    tasks = Task.query.filter_by(is_active=True).all()
    
    # Get completed tasks for this user
    completed_task_ids = [ct.task_id for ct in CompletedTask.query.filter_by(user_id=user_id).all()]
    
    # Filter out expired tasks
    now = datetime.utcnow()
    available_tasks = []
    
    for task in tasks:
        # Skip if task is expired
        if task.expires_at and task.expires_at < now:
            continue
        
        # Skip if task is already completed (for non-repeatable tasks)
        if task.task_type != TaskType.DAILY and task.id in completed_task_ids:
            continue
        
        # For daily tasks, check if completed today
        if task.task_type == TaskType.DAILY:
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            completed_today = CompletedTask.query.filter_by(
                user_id=user_id,
                task_id=task.id
            ).filter(CompletedTask.completed_at >= today_start).first()
            
            if completed_today:
                continue
        
        available_tasks.append({
            "id": task.id,
            "title": task.title_en if user.language == 'en' else task.title_ru,
            "description": task.description_en if user.language == 'en' else task.description_ru,
            "type": task.task_type.value,
            "reward_tokens": task.reward_tokens,
            "required_game_type": task.required_game_type.value if task.required_game_type else None,
            "required_count": task.required_count
        })
    
    return jsonify({"tasks": available_tasks})

@tasks_bp.route('/<int:task_id>/complete', methods=['POST'])
@jwt_required()
def complete_task(task_id):
    """Mark a task as completed"""
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    # Get task
    task = Task.query.get(task_id)
    
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    if not task.is_active:
        return jsonify({"error": "Task is not active"}), 400
    
    # Check if task is expired
    if task.expires_at and task.expires_at < datetime.utcnow():
        return jsonify({"error": "Task has expired"}), 400
    
    # For daily tasks, check if completed today
    if task.task_type == TaskType.DAILY:
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        completed_today = CompletedTask.query.filter_by(
            user_id=user_id,
            task_id=task.id
        ).filter(CompletedTask.completed_at >= today_start).first()
        
        if completed_today:
            return jsonify({"error": "Task already completed today"}), 400
    
    # For non-daily tasks, check if ever completed
    elif task.task_type != TaskType.DAILY:
        completed = CompletedTask.query.filter_by(
            user_id=user_id,
            task_id=task.id
        ).first()
        
        if completed:
            return jsonify({"error": "Task already completed"}), 400
    
    # Check if requirements are met
    if task.required_game_type:
        # For game-related tasks, check game history
        from src.models.models import GameHistory
        
        # If task requires specific game plays, check history
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Time window depends on task type
        if task.task_type == TaskType.DAILY:
            time_window = today_start
        elif task.task_type == TaskType.WEEKLY:
            time_window = today_start - timedelta(days=7)
        else:
            time_window = datetime.min  # All time for achievements
        
        # Count plays
        plays_count = GameHistory.query.filter_by(
            user_id=user_id,
            game_type=task.required_game_type
        ).filter(GameHistory.played_at >= time_window).count()
        
        if plays_count < task.required_count:
            return jsonify({
                "error": "Task requirements not met",
                "required": task.required_count,
                "current": plays_count
            }), 400
    
    # Mark task as completed
    completed_task = CompletedTask(
        user_id=user_id,
        task_id=task.id,
        tokens_awarded=task.reward_tokens
    )
    db.session.add(completed_task)
    
    # Award tokens
    user.flip_tokens += task.reward_tokens
    
    db.session.commit()
    
    return jsonify({
        "message": "Task completed successfully",
        "tokens_awarded": task.reward_tokens,
        "current_balance": user.flip_tokens
    })

@tasks_bp.route('/completed', methods=['GET'])
@jwt_required()
def get_completed_tasks():
    """Get user's completed tasks"""
    user_id = get_jwt_identity()
    
    # Get query parameters
    limit = request.args.get('limit', 10, type=int)
    
    # Get completed tasks
    completed = CompletedTask.query.filter_by(user_id=user_id).order_by(
        CompletedTask.completed_at.desc()
    ).limit(limit).all()
    
    # Get task details
    result = []
    for ct in completed:
        task = Task.query.get(ct.task_id)
        if task:
            result.append({
                "id": ct.id,
                "task_id": task.id,
                "title_en": task.title_en,
                "title_ru": task.title_ru,
                "type": task.task_type.value,
                "tokens_awarded": ct.tokens_awarded,
                "completed_at": ct.completed_at.isoformat()
            })
    
    return jsonify({"completed_tasks": result})

# Admin routes for task management
@tasks_bp.route('/admin', methods=['POST'])
@jwt_required()
def create_task():
    """Create a new task (admin only)"""
    user_id = get_jwt_identity()
    
    if not check_admin_or_tester(user_id):
        return jsonify({"error": "Unauthorized"}), 403
    
    data = request.json
    
    # Validate required fields
    required_fields = ['title_en', 'title_ru', 'description_en', 'description_ru', 
                      'task_type', 'reward_tokens']
    
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), 400
    
    # Parse task type
    try:
        task_type = TaskType(data['task_type'])
    except ValueError:
        return jsonify({"error": "Invalid task type"}), 400
    
    # Parse game type if provided
    required_game_type = None
    if data.get('required_game_type'):
        try:
            required_game_type = GameType(data['required_game_type'])
        except ValueError:
            return jsonify({"error": "Invalid game type"}), 400
    
    # Parse expiration date if provided
    expires_at = None
    if data.get('expires_at'):
        try:
            expires_at = datetime.fromisoformat(data['expires_at'])
        except ValueError:
            return jsonify({"error": "Invalid date format for expires_at"}), 400
    
    # Create task
    task = Task(
        title_en=data['title_en'],
        title_ru=data['title_ru'],
        description_en=data['description_en'],
        description_ru=data['description_ru'],
        task_type=task_type,
        reward_tokens=data['reward_tokens'],
        required_game_type=required_game_type,
        required_count=data.get('required_count', 1),
        is_active=data.get('is_active', True),
        expires_at=expires_at
    )
    
    db.session.add(task)
    db.session.commit()
    
    return jsonify({
        "message": "Task created successfully",
        "task": {
            "id": task.id,
            "title_en": task.title_en,
            "title_ru": task.title_ru,
            "task_type": task.task_type.value,
            "reward_tokens": task.reward_tokens
        }
    }), 201

@tasks_bp.route('/admin/<int:task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    """Update a task (admin only)"""
    user_id = get_jwt_identity()
    
    if not check_admin_or_tester(user_id):
        return jsonify({"error": "Unauthorized"}), 403
    
    task = Task.query.get(task_id)
    
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    data = request.json
    
    # Update fields
    if 'title_en' in data:
        task.title_en = data['title_en']
    if 'title_ru' in data:
        task.title_ru = data['title_ru']
    if 'description_en' in data:
        task.description_en = data['description_en']
    if 'description_ru' in data:
        task.description_ru = data['description_ru']
    if 'reward_tokens' in data:
        task.reward_tokens = data['reward_tokens']
    if 'required_count' in data:
        task.required_count = data['required_count']
    if 'is_active' in data:
        task.is_active = data['is_active']
    
    # Parse task type if provided
    if 'task_type' in data:
        try:
            task.task_type = TaskType(data['task_type'])
        except ValueError:
            return jsonify({"error": "Invalid task type"}), 400
    
    # Parse game type if provided
    if 'required_game_type' in data:
        if data['required_game_type']:
            try:
                task.required_game_type = GameType(data['required_game_type'])
            except ValueError:
                return jsonify({"error": "Invalid game type"}), 400
        else:
            task.required_game_type = None
    
    # Parse expiration date if provided
    if 'expires_at' in data:
        if data['expires_at']:
            try:
                task.expires_at = datetime.fromisoformat(data['expires_at'])
            except ValueError:
                return jsonify({"error": "Invalid date format for expires_at"}), 400
        else:
            task.expires_at = None
    
    db.session.commit()
    
    return jsonify({
        "message": "Task updated successfully",
        "task": {
            "id": task.id,
            "title_en": task.title_en,
            "title_ru": task.title_ru,
            "task_type": task.task_type.value,
            "reward_tokens": task.reward_tokens,
            "is_active": task.is_active
        }
    })

@tasks_bp.route('/admin/<int:task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    """Delete a task (admin only)"""
    user_id = get_jwt_identity()
    
    if not check_admin_or_tester(user_id):
        return jsonify({"error": "Unauthorized"}), 403
    
    task = Task.query.get(task_id)
    
    if not task:
        return jsonify({"error": "Task not found"}), 404
    
    db.session.delete(task)
    db.session.commit()
    
    return jsonify({"message": "Task deleted successfully"})
