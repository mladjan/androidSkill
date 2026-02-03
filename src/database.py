"""Database operations and service layer."""

from datetime import datetime, timedelta
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.models import Agent, Comment, Setting, get_session, init_db
from src.utils import encryption


class DatabaseService:
    """Service class for database operations."""

    def __init__(self):
        """Initialize database service."""
        init_db()

    def create_agent(self, username: str, password: str, email: Optional[str] = None) -> Agent:
        """Create a new agent with encrypted password."""
        session = get_session()
        try:
            # Check if agent already exists
            existing = session.query(Agent).filter_by(username=username).first()
            if existing:
                raise ValueError(f"Agent with username '{username}' already exists")

            # Encrypt password
            encrypted_pwd = encryption.encrypt(password)

            # Create agent
            agent = Agent(
                username=username,
                email=email,
                encrypted_password=encrypted_pwd,
                status="idle",
                comments_today=0,
                comments_total=0
            )

            session.add(agent)
            session.commit()
            session.refresh(agent)
            return agent
        finally:
            session.close()

    def get_agent(self, agent_id: int) -> Optional[Agent]:
        """Get agent by ID."""
        session = get_session()
        try:
            return session.query(Agent).filter_by(id=agent_id).first()
        finally:
            session.close()

    def get_agent_by_username(self, username: str) -> Optional[Agent]:
        """Get agent by username."""
        session = get_session()
        try:
            return session.query(Agent).filter_by(username=username).first()
        finally:
            session.close()

    def list_agents(self) -> List[Agent]:
        """List all agents."""
        session = get_session()
        try:
            return session.query(Agent).order_by(Agent.id).all()
        finally:
            session.close()

    def get_all_agents(self) -> List[Agent]:
        """Get all agents (alias for list_agents)."""
        return self.list_agents()

    def delete_agent(self, agent_id: int) -> bool:
        """Delete agent by ID."""
        session = get_session()
        try:
            agent = session.query(Agent).filter_by(id=agent_id).first()
            if agent:
                session.delete(agent)
                session.commit()
                return True
            return False
        finally:
            session.close()

    def get_agent_password(self, agent_id: int) -> Optional[str]:
        """Get decrypted password for agent."""
        session = get_session()
        try:
            agent = session.query(Agent).filter_by(id=agent_id).first()
            if agent:
                return encryption.decrypt(agent.encrypted_password)
            return None
        finally:
            session.close()

    def update_agent_status(self, agent_id: int, status: str, error_message: Optional[str] = None) -> None:
        """Update agent status."""
        session = get_session()
        try:
            agent = session.query(Agent).filter_by(id=agent_id).first()
            if agent:
                agent.status = status
                agent.last_activity = datetime.utcnow()
                if error_message:
                    agent.last_error = error_message
                session.commit()
        finally:
            session.close()

    def update_agent_next_run(self, agent_id: int, next_run: Optional[datetime]) -> None:
        """Update agent's next scheduled run time."""
        session = get_session()
        try:
            agent = session.query(Agent).filter_by(id=agent_id).first()
            if agent:
                agent.next_run = next_run
                session.commit()
        finally:
            session.close()

    def increment_agent_comments(self, agent_id: int, next_run: Optional[datetime] = None) -> None:
        """Increment agent comment counters."""
        session = get_session()
        try:
            agent = session.query(Agent).filter_by(id=agent_id).first()
            if agent:
                agent.comments_today += 1
                agent.comments_total += 1
                agent.last_activity = datetime.utcnow()
                if next_run:
                    agent.next_run = next_run
                session.commit()
        finally:
            session.close()

    def reset_daily_counters(self) -> None:
        """Reset comments_today counter for all agents (called daily)."""
        session = get_session()
        try:
            session.query(Agent).update({"comments_today": 0})
            session.commit()
        finally:
            session.close()

    def log_comment(
        self,
        agent_id: int,
        video_url: str,
        comment_text: str,
        status: str,
        video_description: Optional[str] = None,
        error_message: Optional[str] = None
    ) -> Comment:
        """Log a comment attempt."""
        session = get_session()
        try:
            comment = Comment(
                agent_id=agent_id,
                video_url=video_url,
                video_description=video_description,
                comment_text=comment_text,
                status=status,
                error_message=error_message
            )
            session.add(comment)
            session.commit()
            session.refresh(comment)
            return comment
        finally:
            session.close()

    def get_recent_comments(self, limit: int = 50) -> List[Comment]:
        """Get recent comments across all agents."""
        session = get_session()
        try:
            return session.query(Comment).order_by(Comment.posted_at.desc()).limit(limit).all()
        finally:
            session.close()

    def get_agent_comments(self, agent_id: int, limit: int = 50) -> List[Comment]:
        """Get recent comments for specific agent."""
        session = get_session()
        try:
            return (
                session.query(Comment)
                .filter_by(agent_id=agent_id)
                .order_by(Comment.posted_at.desc())
                .limit(limit)
                .all()
            )
        finally:
            session.close()

    def get_stats(self) -> dict:
        """Get overall statistics."""
        session = get_session()
        try:
            total_agents = session.query(func.count(Agent.id)).scalar()
            total_comments = session.query(func.count(Comment.id)).scalar()
            comments_today = session.query(func.sum(Agent.comments_today)).scalar() or 0

            successful_comments = (
                session.query(func.count(Comment.id))
                .filter_by(status="posted")
                .scalar()
            )

            success_rate = (successful_comments / total_comments * 100) if total_comments > 0 else 0

            return {
                "total_agents": total_agents,
                "total_comments": total_comments,
                "comments_today": comments_today,
                "success_rate": round(success_rate, 2)
            }
        finally:
            session.close()

    def set_setting(self, key: str, value: str) -> None:
        """Set a configuration setting."""
        session = get_session()
        try:
            setting = session.query(Setting).filter_by(key=key).first()
            if setting:
                setting.value = value
                setting.updated_at = datetime.utcnow()
            else:
                setting = Setting(key=key, value=value)
                session.add(setting)
            session.commit()
        finally:
            session.close()

    def get_setting(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get a configuration setting."""
        session = get_session()
        try:
            setting = session.query(Setting).filter_by(key=key).first()
            return setting.value if setting else default
        finally:
            session.close()


# Singleton instance
db = DatabaseService()
