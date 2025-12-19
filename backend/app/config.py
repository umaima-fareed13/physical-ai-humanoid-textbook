"""Application configuration using Pydantic Settings."""

from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Google Gemini (primary)
    google_api_key: str

    # OpenAI (optional fallback)
    openai_api_key: str = ""

    # Qdrant Cloud
    qdrant_url: str
    qdrant_api_key: str

    # Neon Postgres
    neon_database_url: str

    # Application
    docs_path: str = "../docs"
    embedding_model: str = "models/text-embedding-004"  # Google embedding model
    chat_model: str = "gemini-1.5-flash"  # Google chat model

    # CORS
    cors_origins: str = "http://localhost:3000"

    # Qdrant Collection
    collection_name: str = "physical_ai_textbook"
    vector_size: int = 768  # Google text-embedding-004 dimension

    # Chunking
    chunk_size: int = 500
    chunk_overlap: int = 50

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
