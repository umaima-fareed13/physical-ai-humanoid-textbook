"""Pydantic schemas for API request/response validation."""

from datetime import datetime

from pydantic import BaseModel, Field


# =============================================================================
# Chat Schemas
# =============================================================================


class ChatRequest(BaseModel):
    """Request schema for chat endpoint."""

    message: str = Field(..., min_length=1, max_length=4000)
    session_id: str = Field(..., min_length=1, max_length=36)
    selected_text: str | None = Field(
        default=None,
        max_length=2000,
        description="User-highlighted text for context",
    )


class SourceReference(BaseModel):
    """Source reference from RAG retrieval."""

    file: str
    chunk: str
    score: float | None = None


class ChatResponse(BaseModel):
    """Response schema for chat endpoint."""

    response: str
    sources: list[SourceReference] = []
    session_id: str


class MessageSchema(BaseModel):
    """Schema for a single chat message."""

    id: int | None = None
    role: str
    content: str
    selected_text: str | None = None
    sources: list[SourceReference] | None = None
    created_at: datetime | None = None

    class Config:
        from_attributes = True


class ConversationHistory(BaseModel):
    """Schema for conversation history."""

    session_id: str
    messages: list[MessageSchema] = []


# =============================================================================
# Ingest Schemas
# =============================================================================


class IngestRequest(BaseModel):
    """Request schema for ingest endpoint."""

    file: str | None = Field(
        default=None,
        description="Specific file to ingest (e.g., 'chapter-1.md'). If not provided, ingest all.",
    )


class ChunkInfo(BaseModel):
    """Information about a processed chunk."""

    text: str
    source: str
    position: int
    title: str | None = None


class IngestResponse(BaseModel):
    """Response schema for ingest endpoint."""

    status: str
    chunks_processed: int
    files: list[str]
    message: str | None = None


# =============================================================================
# Health Check Schemas
# =============================================================================


class HealthCheck(BaseModel):
    """Health check response schema."""

    status: str
    database: str = "unknown"
    vectordb: str = "unknown"
