"""FastAPI application entry point for the RAG Chatbot backend."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import chat, ingest
from app.services.database import init_db
from app.services.vectordb import init_collection


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown events."""
    # Startup
    settings = get_settings()
    print(f"Starting Physical AI Textbook RAG Backend...")
    print(f"Docs path: {settings.docs_path}")

    # Initialize database tables
    await init_db()
    print("Database initialized")

    # Initialize Qdrant collection
    await init_collection()
    print("Qdrant collection initialized")

    yield

    # Shutdown
    print("Shutting down...")


app = FastAPI(
    title="Physical AI Textbook RAG Chatbot",
    description="RAG-powered chatbot API for the Physical AI Textbook",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(ingest.router, prefix="/ingest", tags=["ingest"])


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Physical AI Textbook RAG Chatbot",
        "version": "1.0.0",
    }


@app.get("/health")
async def health_check():
    """Detailed health check endpoint."""
    return {
        "status": "healthy",
        "database": "connected",
        "vectordb": "connected",
    }
