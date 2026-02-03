"""Database models for agents, comments, and settings."""

from datetime import datetime
from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, LargeBinary, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

from src.config import config

Base = declarative_base()


class Agent(Base):
    """TikTok account model."""

    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), nullable=True)
    encrypted_password = Column(LargeBinary, nullable=False)
    status = Column(String(20), default="idle", nullable=False)  # idle, active, banned, error
    comments_today = Column(Integer, default=0, nullable=False)
    comments_total = Column(Integer, default=0, nullable=False)
    last_activity = Column(DateTime, nullable=True)
    last_error = Column(Text, nullable=True)
    next_run = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    comments = relationship("Comment", back_populates="agent", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Agent(id={self.id}, username='{self.username}', status='{self.status}')>"


class Comment(Base):
    """Comment activity log model."""

    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_id = Column(Integer, ForeignKey("agents.id", ondelete="CASCADE"), nullable=False)
    video_url = Column(Text, nullable=False)
    video_description = Column(Text, nullable=True)
    comment_text = Column(Text, nullable=False)
    status = Column(String(20), nullable=False)  # posted, failed, detected
    error_message = Column(Text, nullable=True)
    posted_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    agent = relationship("Agent", back_populates="comments")

    def __repr__(self):
        return f"<Comment(id={self.id}, agent_id={self.agent_id}, status='{self.status}')>"


class Setting(Base):
    """Application settings model."""

    __tablename__ = "settings"

    key = Column(String(100), primary_key=True)
    value = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<Setting(key='{self.key}', value='{self.value}')>"


# Database setup
def get_engine():
    """Create and return database engine."""
    db_url = config.DATABASE_URL
    return create_engine(db_url, echo=False, connect_args={"check_same_thread": False} if "sqlite" in db_url else {})


def get_session():
    """Create and return database session."""
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()


def init_db():
    """Initialize database and create all tables."""
    engine = get_engine()
    Base.metadata.create_all(engine)
