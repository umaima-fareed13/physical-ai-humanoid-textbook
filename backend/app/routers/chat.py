"""Chat router for handling RAG-powered conversations."""

from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    ChatRequest,
    ChatResponse,
    ConversationHistory,
    MessageSchema,
    SourceReference,
)
from app.services.database import (
    get_conversation_for_context,
    get_session_history,
    save_message,
)
from app.services.rag import chat

router = APIRouter()


@router.post("", response_model=ChatResponse)
async def send_message(request: ChatRequest):
    """Send a message to the chatbot and get a RAG-powered response.

    The endpoint:
    1. Retrieves conversation history for context
    2. Saves the user message
    3. Performs RAG retrieval from the textbook
    4. Generates a response using the LLM
    5. Saves the assistant response
    6. Returns the response with source citations
    """
    try:
        # Get conversation history for context
        history = await get_conversation_for_context(
            session_id=request.session_id,
            limit=5,
        )

        # Save user message
        await save_message(
            session_id=request.session_id,
            role="user",
            content=request.message,
            selected_text=request.selected_text,
        )

        # Generate RAG response
        response_text, sources = await chat(
            query=request.message,
            session_id=request.session_id,
            selected_text=request.selected_text,
            conversation_history=history,
        )

        # Convert sources to proper format for storage
        sources_for_db = [
            {"file": s["file"], "chunk": s["chunk"], "score": s.get("score")}
            for s in sources
        ]

        # Save assistant response
        await save_message(
            session_id=request.session_id,
            role="assistant",
            content=response_text,
            sources=sources_for_db,
        )

        # Return response
        return ChatResponse(
            response=response_text,
            sources=[
                SourceReference(
                    file=s["file"],
                    chunk=s["chunk"],
                    score=s.get("score"),
                )
                for s in sources
            ],
            session_id=request.session_id,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Chat failed: {str(e)}",
        )


@router.get("/history/{session_id}", response_model=ConversationHistory)
async def get_history(session_id: str, limit: int = 50):
    """Get conversation history for a session.

    Args:
        session_id: The session ID
        limit: Maximum number of messages to return
    """
    try:
        messages = await get_session_history(session_id, limit=limit)

        return ConversationHistory(
            session_id=session_id,
            messages=[
                MessageSchema(
                    id=msg.id,
                    role=msg.role,
                    content=msg.content,
                    selected_text=msg.selected_text,
                    sources=[
                        SourceReference(**s) for s in (msg.sources or [])
                    ] if msg.sources else None,
                    created_at=msg.created_at,
                )
                for msg in messages
            ],
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get history: {str(e)}",
        )


@router.delete("/history/{session_id}")
async def clear_history(session_id: str):
    """Clear conversation history for a session.

    Note: This doesn't delete the session, just the messages.
    """
    from sqlalchemy import delete

    from app.models.database import Message
    from app.services.database import get_session_factory

    try:
        SessionLocal = get_session_factory()
        db = SessionLocal()
        try:
            db.query(Message).filter(Message.session_id == session_id).delete()
            db.commit()
            return {"status": "success", "message": "History cleared"}
        finally:
            db.close()

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear history: {str(e)}",
        )
