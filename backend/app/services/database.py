"""Neon Postgres database service for session and message storage."""

from datetime import datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import Session as SQLSession
from sqlalchemy.orm import sessionmaker

from app.config import get_settings
from app.models.database import Base, Message, Session

# Engine and session factory
_engine = None
_SessionLocal = None


def get_engine():
    """Get or create database engine."""
    global _engine
    if _engine is None:
        settings = get_settings()
        _engine = create_engine(
            settings.neon_database_url,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
        )
    return _engine


def get_session_factory():
    """Get or create session factory."""
    global _SessionLocal
    if _SessionLocal is None:
        engine = get_engine()
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return _SessionLocal


async def init_db() -> None:
    """Initialize database tables."""
    engine = get_engine()
    Base.metadata.create_all(bind=engine)


def get_db() -> SQLSession:
    """Get database session (dependency for FastAPI)."""
    SessionLocal = get_session_factory()
    db = SessionLocal()
    try:
        return db
    finally:
        pass  # Session will be closed by caller


# =============================================================================
# Session Operations
# =============================================================================


async def get_or_create_session(session_id: str) -> Session:
    """Get existing session or create a new one.

    Args:
        session_id: Browser-generated session ID

    Returns:
        Session object
    """
    SessionLocal = get_session_factory()
    db = SessionLocal()
    try:
        session = db.query(Session).filter(Session.id == session_id).first()

        if session is None:
            session = Session(id=session_id)
            db.add(session)
            db.commit()
            db.refresh(session)
        else:
            # Update last_active
            session.last_active = datetime.utcnow()
            db.commit()

        return session
    finally:
        db.close()


async def get_session_history(
    session_id: str,
    limit: int = 20,
) -> list[Message]:
    """Get recent messages for a session.

    Args:
        session_id: Session ID
        limit: Maximum number of messages to return

    Returns:
        List of messages ordered by creation time
    """
    SessionLocal = get_session_factory()
    db = SessionLocal()
    try:
        messages = (
            db.query(Message)
            .filter(Message.session_id == session_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
            .all()
        )
        # Reverse to get chronological order
        return list(reversed(messages))
    finally:
        db.close()


# =============================================================================
# Message Operations
# =============================================================================


async def save_message(
    session_id: str,
    role: str,
    content: str,
    selected_text: str | None = None,
    sources: list[dict] | None = None,
) -> Message:
    """Save a chat message.

    Args:
        session_id: Session ID
        role: 'user' or 'assistant'
        content: Message content
        selected_text: User-highlighted text (for user messages)
        sources: Source references (for assistant messages)

    Returns:
        Created message object
    """
    SessionLocal = get_session_factory()
    db = SessionLocal()
    try:
        # Ensure session exists
        await get_or_create_session(session_id)

        message = Message(
            session_id=session_id,
            role=role,
            content=content,
            selected_text=selected_text,
            sources=sources,
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        return message
    finally:
        db.close()


async def get_conversation_for_context(
    session_id: str,
    limit: int = 10,
) -> list[dict]:
    """Get recent conversation formatted for LLM context.

    Args:
        session_id: Session ID
        limit: Maximum number of message pairs

    Returns:
        List of message dicts with 'role' and 'content'
    """
    messages = await get_session_history(session_id, limit=limit * 2)

    return [
        {
            "role": msg.role,
            "content": msg.content,
        }
        for msg in messages
    ]
