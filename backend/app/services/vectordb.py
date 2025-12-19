"""Qdrant vector database service for document storage and retrieval."""

import uuid

from qdrant_client import QdrantClient
from qdrant_client.http import models

from app.config import get_settings

# Initialize Qdrant client lazily
_client: QdrantClient | None = None


def get_qdrant_client() -> QdrantClient:
    """Get or create Qdrant client instance."""
    global _client
    if _client is None:
        settings = get_settings()
        _client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
        )
    return _client


async def init_collection() -> None:
    """Initialize Qdrant collection if it doesn't exist."""
    settings = get_settings()
    client = get_qdrant_client()

    # Check if collection exists
    collections = client.get_collections()
    collection_names = [c.name for c in collections.collections]

    if settings.collection_name not in collection_names:
        # Create collection
        client.create_collection(
            collection_name=settings.collection_name,
            vectors_config=models.VectorParams(
                size=settings.vector_size,
                distance=models.Distance.COSINE,
            ),
        )
        print(f"Created collection: {settings.collection_name}")
    else:
        print(f"Collection already exists: {settings.collection_name}")


async def delete_collection() -> None:
    """Delete the Qdrant collection (for re-ingestion)."""
    settings = get_settings()
    client = get_qdrant_client()

    try:
        client.delete_collection(collection_name=settings.collection_name)
        print(f"Deleted collection: {settings.collection_name}")
    except Exception as e:
        print(f"Error deleting collection: {e}")


async def upsert_chunks(
    chunks: list[dict],
    vectors: list[list[float]],
) -> int:
    """Upsert document chunks with their embeddings to Qdrant.

    Args:
        chunks: List of chunk dictionaries with 'text', 'source', 'position', 'title'
        vectors: Corresponding embedding vectors

    Returns:
        Number of points upserted
    """
    settings = get_settings()
    client = get_qdrant_client()

    if len(chunks) != len(vectors):
        raise ValueError("Number of chunks must match number of vectors")

    # Create points
    points = []
    for chunk, vector in zip(chunks, vectors):
        point_id = str(uuid.uuid4())
        points.append(
            models.PointStruct(
                id=point_id,
                vector=vector,
                payload={
                    "text": chunk["text"],
                    "source": chunk["source"],
                    "position": chunk["position"],
                    "title": chunk.get("title", ""),
                },
            )
        )

    # Upsert in batches
    batch_size = 100
    for i in range(0, len(points), batch_size):
        batch = points[i : i + batch_size]
        client.upsert(
            collection_name=settings.collection_name,
            points=batch,
        )

    return len(points)


async def search(
    query_vector: list[float],
    limit: int = 5,
    score_threshold: float = 0.5,
) -> list[dict]:
    """Search for similar documents in Qdrant.

    Args:
        query_vector: Query embedding vector
        limit: Maximum number of results
        score_threshold: Minimum similarity score

    Returns:
        List of matching documents with scores
    """
    settings = get_settings()
    client = get_qdrant_client()

    results = client.search(
        collection_name=settings.collection_name,
        query_vector=query_vector,
        limit=limit,
        score_threshold=score_threshold,
    )

    return [
        {
            "text": hit.payload.get("text", ""),
            "source": hit.payload.get("source", ""),
            "position": hit.payload.get("position", 0),
            "title": hit.payload.get("title", ""),
            "score": hit.score,
        }
        for hit in results
    ]


async def get_collection_info() -> dict:
    """Get information about the collection."""
    settings = get_settings()
    client = get_qdrant_client()

    try:
        info = client.get_collection(collection_name=settings.collection_name)
        return {
            "name": settings.collection_name,
            "vectors_count": info.vectors_count,
            "points_count": info.points_count,
            "status": info.status.value,
        }
    except Exception as e:
        return {"error": str(e)}
