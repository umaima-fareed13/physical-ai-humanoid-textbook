"""Google Gemini embeddings service with retry logic."""

import time
import google.generativeai as genai

from app.config import get_settings

# Rate limiting configuration
MAX_RETRIES = 5
INITIAL_DELAY = 5  # seconds
MAX_DELAY = 60  # seconds


def get_genai_configured():
    """Ensure genai is configured."""
    settings = get_settings()
    genai.configure(api_key=settings.google_api_key)


async def embed_text(text: str) -> list[float]:
    """Generate embedding for a single text with retry logic.

    Args:
        text: Text to embed

    Returns:
        Embedding vector as list of floats
    """
    get_genai_configured()
    settings = get_settings()

    # Truncate text if too long
    max_chars = 5000
    if len(text) > max_chars:
        text = text[:max_chars]

    delay = INITIAL_DELAY
    for attempt in range(MAX_RETRIES):
        try:
            result = genai.embed_content(
                model=settings.embedding_model,
                content=text,
                task_type="retrieval_document",
            )
            return result['embedding']
        except Exception as e:
            if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                if attempt < MAX_RETRIES - 1:
                    print(f"Rate limited, waiting {delay}s before retry {attempt + 2}/{MAX_RETRIES}...")
                    time.sleep(delay)
                    delay = min(delay * 2, MAX_DELAY)
                else:
                    raise
            else:
                raise


async def embed_batch(texts: list[str], batch_size: int = 1) -> list[list[float]]:
    """Generate embeddings for multiple texts one at a time with rate limiting.

    Args:
        texts: List of texts to embed
        batch_size: Ignored, always processes one at a time for rate limiting

    Returns:
        List of embedding vectors
    """
    get_genai_configured()
    settings = get_settings()

    # Truncate texts if needed
    max_chars = 5000
    texts = [t[:max_chars] if len(t) > max_chars else t for t in texts]

    print(f"Generating embeddings for {len(texts)} texts (with rate limiting)...")

    all_embeddings = []
    delay = 2  # Base delay between requests

    for i, text in enumerate(texts):
        # Rate limit: wait between requests
        if i > 0:
            time.sleep(delay)

        retry_delay = INITIAL_DELAY
        for attempt in range(MAX_RETRIES):
            try:
                result = genai.embed_content(
                    model=settings.embedding_model,
                    content=text,
                    task_type="retrieval_document",
                )
                all_embeddings.append(result['embedding'])
                print(f"  Embedded {i + 1}/{len(texts)}")
                break
            except Exception as e:
                if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
                    if attempt < MAX_RETRIES - 1:
                        print(f"  Rate limited at {i + 1}, waiting {retry_delay}s...")
                        time.sleep(retry_delay)
                        retry_delay = min(retry_delay * 2, MAX_DELAY)
                    else:
                        print(f"  Failed after {MAX_RETRIES} retries")
                        raise
                else:
                    raise

    print(f"Generated {len(all_embeddings)} embeddings")
    return all_embeddings
