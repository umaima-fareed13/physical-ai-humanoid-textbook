"""SQLAlchemy database models for session and message storage."""

from datetime import datetime

from sqlalchemy import (
    JSON,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    create_engine,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Session(Base):
    """User session model for tracking anonymous chat sessions."""

    __tablename__ = "sessions"

    id = Column(String(36), primary_key=True)  # UUID from browser
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_active = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # Relationship to messages
    messages = relationship(
        "Message",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="Message.created_at",
    )

    def __repr__(self):
        return f"<Session(id={self.id}, created_at={self.created_at})>"


class Message(Base):
    """Chat message model for storing conversation history."""

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(
        String(36),
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    selected_text = Column(Text, nullable=True)  # User-highlighted text context
    sources = Column(JSON, nullable=True)  # Source citations for assistant messages
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationship to session
    session = relationship("Session", back_populates="messages")

    def __repr__(self):
        return f"<Message(id={self.id}, role={self.role}, session_id={self.session_id})>"

    def to_dict(self):
        """Convert message to dictionary for API responses."""
        return {
            "id": self.id,
            "role": self.role,
            "content": self.content,
            "selected_text": self.selected_text,
            "sources": self.sources,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
