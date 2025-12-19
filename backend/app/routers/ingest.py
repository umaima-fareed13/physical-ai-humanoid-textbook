"""Ingest router for processing book content into vector database."""

from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.config import get_settings
from app.models.schemas import IngestRequest, IngestResponse
from app.services.embeddings import embed_batch
from app.services.vectordb import delete_collection, get_collection_info, init_collection, upsert_chunks
from app.utils.markdown import get_all_docs, parse_markdown_file, process_all_docs

router = APIRouter()


@router.post("", response_model=IngestResponse)
async def ingest_documents(request: IngestRequest | None = None):
    """Ingest markdown documents into the vector database.

    If a specific file is provided, only that file is ingested.
    Otherwise, all .md files in the docs directory are processed.

    This endpoint:
    1. Reads markdown files from the docs directory
    2. Chunks the content into smaller pieces
    3. Generates embeddings using OpenAI
    4. Stores vectors in Qdrant for retrieval
    """
    settings = get_settings()
    request = request or IngestRequest()

    try:
        if request.file:
            # Ingest single file
            docs_path = Path(settings.docs_path)
            if not docs_path.is_absolute():
                base_dir = Path(__file__).parent.parent.parent
                docs_path = base_dir / docs_path

            filepath = docs_path / request.file
            if not filepath.exists():
                raise HTTPException(
                    status_code=404,
                    detail=f"File not found: {request.file}",
                )

            parsed = parse_markdown_file(str(filepath))
            chunks = [
                {
                    "text": chunk_text,
                    "source": parsed["source"],
                    "position": i,
                    "title": parsed["title"],
                }
                for i, chunk_text in enumerate(parsed["chunks"])
            ]
            files_processed = [request.file]
        else:
            # Ingest all documents - recreate collection for clean slate
            await delete_collection()
            await init_collection()

            chunks = process_all_docs()
            files_processed = list(set(chunk["source"] for chunk in chunks))

        if not chunks:
            return IngestResponse(
                status="success",
                chunks_processed=0,
                files=files_processed,
                message="No content found to ingest",
            )

        # Generate embeddings for all chunks
        texts = [chunk["text"] for chunk in chunks]
        print(f"Generating embeddings for {len(texts)} chunks...")
        vectors = await embed_batch(texts)

        # Upsert to Qdrant
        print(f"Upserting {len(chunks)} chunks to Qdrant...")
        count = await upsert_chunks(chunks, vectors)

        return IngestResponse(
            status="success",
            chunks_processed=count,
            files=files_processed,
            message=f"Successfully ingested {count} chunks from {len(files_processed)} file(s)",
        )

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ingestion failed: {str(e)}",
        )


@router.get("/status")
async def get_ingest_status():
    """Get the current status of the vector database."""
    try:
        info = await get_collection_info()
        docs = get_all_docs()

        return {
            "collection": info,
            "available_docs": [Path(d).name for d in docs],
            "docs_count": len(docs),
        }
    except Exception as e:
        return {
            "error": str(e),
            "collection": None,
            "available_docs": [],
        }


@router.delete("")
async def clear_vectors():
    """Clear all vectors from the database (for re-ingestion)."""
    try:
        await delete_collection()
        await init_collection()
        return {"status": "success", "message": "Collection cleared and recreated"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to clear collection: {str(e)}",
        )
