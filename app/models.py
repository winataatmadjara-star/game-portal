from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey, Index
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


# ============================================================
# USER
# ============================================================
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    phone = Column(String(30), nullable=True, default='-')
    role = Column(String(30), default='Free', nullable=False)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Relasi
    scores = relationship("GameScore", back_populates="user", cascade="all, delete-orphan")
    achievements = relationship("UserAchievement", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"


# ============================================================
# GAME
# ============================================================
class Game(Base):
    __tablename__ = 'games'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(150), index=True, nullable=False)
    slug = Column(String(150), unique=True, index=True, nullable=False)
    category = Column(String(50), nullable=False, index=True)
    description = Column(Text, nullable=True)
    thumbnail = Column(String(255), nullable=True)
    embed_url = Column(String(255), nullable=False)
    views = Column(Integer, default=0, nullable=False)
    is_active = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Relasi
    scores = relationship("GameScore", back_populates="game", cascade="all, delete-orphan")

    __table_args__ = (
        Index('ix_games_category_active', 'category', 'is_active'),
    )

    def __repr__(self):
        return f"<Game {self.title} [{self.category}]>"


# ============================================================
# GAME SCORE
# ============================================================
class GameScore(Base):
    __tablename__ = 'game_scores'

    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey('games.id', ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    score = Column(Integer, nullable=False, default=0)
    max_level = Column(Integer, nullable=False, default=0)   # BARU: level tertinggi yang dicapai
    won = Column(Integer, nullable=False, default=0)         # BARU: 1 kalau tamat, 0 kalau tidak
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Relasi balik
    game = relationship("Game", back_populates="scores")
    user = relationship("User", back_populates="scores")

    __table_args__ = (
        Index('ix_scores_game_score', 'game_id', 'score'),
        Index('ix_scores_user_created', 'user_id', 'created_at'),
    )

    def __repr__(self):
        return f"<GameScore game_id={self.game_id} score={self.score} level={self.max_level} won={self.won}>"


# ============================================================
# LOGIN ATTEMPT — untuk rate limiting anti-bot
# ============================================================
class LoginAttempt(Base):
    __tablename__ = 'login_attempts'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False, index=True)
    ip_address = Column(String(45), nullable=False, index=True)
    success = Column(Integer, default=0, nullable=False)
    user_agent = Column(String(255), nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False, index=True)

    __table_args__ = (
        Index('ix_login_attempts_username_time', 'username', 'created_at'),
        Index('ix_login_attempts_ip_time', 'ip_address', 'created_at'),
    )

    def __repr__(self):
        return f"<LoginAttempt {self.username}@{self.ip_address} success={self.success}>"


# ============================================================
# ACHIEVEMENT
# ============================================================
class Achievement(Base):
    __tablename__ = 'achievements'

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(100), nullable=False)
    description = Column(String(255), nullable=False)
    icon = Column(String(10), nullable=False, default='🏆')
    category = Column(String(30), nullable=False, default='general')
    tier = Column(String(20), nullable=False, default='rookie')       # BARU: rookie | pro | legend
    points = Column(Integer, default=10, nullable=False)
    condition_type = Column(String(30), nullable=False)
    condition_value = Column(Integer, default=0, nullable=False)
    condition_slug = Column(String(50), nullable=True)
    is_secret = Column(Integer, default=0, nullable=False)            # BARU: 1 kalau achievement rahasia
    is_active = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Relasi
    unlocks = relationship("UserAchievement", back_populates="achievement", cascade="all, delete-orphan")

    __table_args__ = (
        Index('ix_achievements_tier_category', 'tier', 'category'),
    )

    def __repr__(self):
        return f"<Achievement {self.slug} [{self.tier}]>"


# ============================================================
# USER ACHIEVEMENT — track achievement yang sudah dibuka user
# ============================================================
class UserAchievement(Base):
    __tablename__ = 'user_achievements'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    achievement_id = Column(Integer, ForeignKey('achievements.id', ondelete='CASCADE'), nullable=False)
    unlocked_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Relasi
    user = relationship("User", back_populates="achievements")
    achievement = relationship("Achievement", back_populates="unlocks")

    __table_args__ = (
        Index('ix_user_achievement_unique', 'user_id', 'achievement_id', unique=True),
    )

    def __repr__(self):
        return f"<UserAchievement user={self.user_id} ach={self.achievement_id}>"