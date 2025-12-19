"""Standalone script to run document ingestion into Qdrant."""

import asyncio
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.config import get_settings
from app.services.embeddings import embed_batch
from app.services.vectordb import delete_collection, init_collection, upsert_chunks
from app.utils.markdown import process_all_docs


async def run_ingestion():
    """Run the full ingestion pipeline."""
    settings = get_settings()

    print("=" * 50)
    print("Physical AI Textbook - Document Ingestion")
    print("=" * 50)
    print(f"Docs path: {settings.docs_path}")
    print(f"Embedding model: {settings.embedding_model}")
    print(f"Qdrant collection: {settings.collection_name}")
    print("=" * 50)

    # Step 1: Delete and recreate collection
    print("\n[1/4] Resetting Qdrant collection...")
    try:
        await delete_collection()
    except Exception as e:
        print(f"  Note: {e}")
    await init_collection()
    print("  Done!")

    # Step 2: Process markdown files
    print("\n[2/4] Processing markdown files...")
    chunks = process_all_docs()
    files_processed = list(set(chunk["source"] for chunk in chunks))
    print(f"  Found {len(chunks)} chunks from {len(files_processed)} files:")
    for f in files_processed:
        print(f"    - {f}")

    if not chunks:
        print("  No content found to ingest!")
        return

    # Step 3: Generate embeddings
    print(f"\n[3/4] Generating embeddings for {len(chunks)} chunks...")
    texts = [chunk["text"] for chunk in chunks]
    vectors = await embed_batch(texts)
    print(f"  Generated {len(vectors)} embeddings")

    # Step 4: Upsert to Qdrant
    print(f"\n[4/4] Upserting to Qdrant...")
    count = await upsert_chunks(chunks, vectors)
    print(f"  Upserted {count} vectors")

    print("\n" + "=" * 50)
    print("Ingestion complete!")
    print(f"  Files: {len(files_processed)}")
    print(f"  Chunks: {count}")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(run_ingestion())
