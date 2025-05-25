from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import enum

db = SQLAlchemy()

class UserRole(enum.Enum):
    ADMIN = "admin"
    TESTER = "tester"
    USER = "user"

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    telegram_id = db.Column(db.String(20), unique=True, nullable=False)
    username = db.Column(db.String(100), nullable=True)
    first_name = db.Column(db.String(100), nullable=True)
    last_name = db.Column(db.String(100), nullable=True)
    nickname = db.Column(db.String(100), nullable=False)
    flip_tokens = db.Column(db.Integer, default=100)
    language = db.Column(db.String(2), default='en')
    sound_enabled = db.Column(db.Boolean, default=True)
    role = db.Column(db.Enum(UserRole), default=UserRole.USER)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    game_history = db.relationship('GameHistory', backref='user', lazy=True)
    completed_tasks = db.relationship('CompletedTask', backref='user', lazy=True)
    redeemed_rewards = db.relationship('RedeemedReward', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.nickname}>'

class Referral(db.Model):
    __tablename__ = 'referrals'
    
    id = db.Column(db.Integer, primary_key=True)
    referrer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    referred_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reward_given = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    referrer = db.relationship('User', foreign_keys=[referrer_id], backref='referrals_made')
    referred = db.relationship('User', foreign_keys=[referred_id], backref='referred_by')
    
    def __repr__(self):
        return f'<Referral {self.referrer_id} -> {self.referred_id}>'

class GameType(enum.Enum):
    FLIP_COIN = "flip_coin"
    MAGIC_BALL = "magic_ball"
    TAROT_CARD = "tarot_card"

class GameHistory(db.Model):
    __tablename__ = 'game_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    game_type = db.Column(db.Enum(GameType), nullable=False)
    result = db.Column(db.String(100), nullable=False)
    tokens_earned = db.Column(db.Integer, default=0)
    played_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<GameHistory {self.game_type.value} by {self.user_id}>'

class TaskType(enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    ACHIEVEMENT = "achievement"
    SPECIAL = "special"

class Task(db.Model):
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    title_en = db.Column(db.String(100), nullable=False)
    title_ru = db.Column(db.String(100), nullable=False)
    description_en = db.Column(db.Text, nullable=False)
    description_ru = db.Column(db.Text, nullable=False)
    task_type = db.Column(db.Enum(TaskType), nullable=False)
    reward_tokens = db.Column(db.Integer, nullable=False)
    required_game_type = db.Column(db.Enum(GameType), nullable=True)
    required_count = db.Column(db.Integer, default=1)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    completed = db.relationship('CompletedTask', backref='task', lazy=True)
    
    def __repr__(self):
        return f'<Task {self.title_en}>'

class CompletedTask(db.Model):
    __tablename__ = 'completed_tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    tokens_awarded = db.Column(db.Integer, nullable=False)
    
    def __repr__(self):
        return f'<CompletedTask {self.task_id} by {self.user_id}>'

class Reward(db.Model):
    __tablename__ = 'rewards'
    
    id = db.Column(db.Integer, primary_key=True)
    name_en = db.Column(db.String(100), nullable=False)
    name_ru = db.Column(db.String(100), nullable=False)
    description_en = db.Column(db.Text, nullable=False)
    description_ru = db.Column(db.Text, nullable=False)
    image = db.Column(db.String(255), nullable=True)
    cost = db.Column(db.Integer, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    stock = db.Column(db.Integer, nullable=True)  # NULL means unlimited
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    redeemed = db.relationship('RedeemedReward', backref='reward', lazy=True)
    
    def __repr__(self):
        return f'<Reward {self.name_en}>'

class RedeemedReward(db.Model):
    __tablename__ = 'redeemed_rewards'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reward_id = db.Column(db.Integer, db.ForeignKey('rewards.id'), nullable=False)
    redeemed_at = db.Column(db.DateTime, default=datetime.utcnow)
    tokens_spent = db.Column(db.Integer, nullable=False)
    
    def __repr__(self):
        return f'<RedeemedReward {self.reward_id} by {self.user_id}>'

class PaymentStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    telegram_payment_id = db.Column(db.String(100), nullable=True)
    amount = db.Column(db.Float, nullable=False)
    tokens_amount = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Enum(PaymentStatus), default=PaymentStatus.PENDING)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<Payment {self.id} by {self.user_id}>'

class DailyLimit(db.Model):
    __tablename__ = 'daily_limits'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    game_type = db.Column(db.Enum(GameType), nullable=False)
    count = db.Column(db.Integer, default=0)
    date = db.Column(db.Date, nullable=False)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'game_type', 'date', name='unique_daily_limit'),
    )
    
    def __repr__(self):
        return f'<DailyLimit {self.game_type.value} for {self.user_id} on {self.date}>'
