"""Markdown parsing and chunking utilities for document processing."""

import os
import re
from pathlib import Path

import markdown
from bs4 import BeautifulSoup

from app.config import get_settings


def extract_frontmatter(content: str) -> tuple[dict, str]:
    """Extract YAML frontmatter from markdown content.

    Args:
        content: Raw markdown content

    Returns:
        Tuple of (frontmatter dict, remaining content)
    """
    frontmatter = {}
    body = content

    # Match YAML frontmatter between --- markers
    pattern = r"^---\s*\n(.*?)\n---\s*\n"
    match = re.match(pattern, content, re.DOTALL)

    if match:
        frontmatter_text = match.group(1)
        body = content[match.end() :]

        # Parse simple YAML (key: value pairs)
        for line in frontmatter_text.split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip().strip("'\"")
                frontmatter[key] = value

    return frontmatter, body


def markdown_to_text(content: str) -> str:
    """Convert markdown content to plain text.

    Args:
        content: Markdown content

    Returns:
        Plain text with formatting removed
    """
    # Convert markdown to HTML
    html = markdown.markdown(content, extensions=["tables", "fenced_code"])

    # Parse HTML and extract text
    soup = BeautifulSoup(html, "html.parser")

    # Remove code blocks (keep them but mark them)
    for code in soup.find_all(["pre", "code"]):
        code.replace_with(f" [CODE: {code.get_text()}] ")

    # Get text
    text = soup.get_text(separator=" ")

    # Clean up whitespace
    text = re.sub(r"\s+", " ", text)
    text = text.strip()

    return text


def chunk_text(
    text: str,
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[str]:
    """Split text into overlapping chunks.

    Args:
        text: Text to chunk
        chunk_size: Maximum characters per chunk
        overlap: Number of overlapping characters between chunks

    Returns:
        List of text chunks
    """
    settings = get_settings()
    chunk_size = chunk_size or settings.chunk_size
    overlap = overlap or settings.chunk_overlap

    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        # Try to break at sentence boundary
        if end < len(text):
            # Look for sentence end within last 100 chars of chunk
            search_start = max(end - 100, start)
            last_period = text.rfind(". ", search_start, end)
            last_newline = text.rfind("\n", search_start, end)
            break_point = max(last_period, last_newline)

            if break_point > start:
                end = break_point + 1

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        # Move start position with overlap
        start = end - overlap

    return chunks


def parse_markdown_file(filepath: str) -> dict:
    """Parse a markdown file into metadata and chunks.

    Args:
        filepath: Path to markdown file

    Returns:
        Dict with 'title', 'source', and 'chunks' keys
    """
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract frontmatter and body
    frontmatter, body = extract_frontmatter(content)

    # Get title from frontmatter or filename
    title = frontmatter.get("title") or frontmatter.get("sidebar_label")
    if not title:
        title = Path(filepath).stem.replace("-", " ").title()

    # Convert to plain text
    plain_text = markdown_to_text(body)

    # Chunk the text
    chunks = chunk_text(plain_text)

    return {
        "title": title,
        "source": Path(filepath).name,
        "frontmatter": frontmatter,
        "chunks": chunks,
    }


def get_all_docs(docs_path: str | None = None) -> list[str]:
    """Get all markdown files from the docs directory.

    Args:
        docs_path: Path to docs directory (uses config default if not provided)

    Returns:
        List of absolute file paths to markdown files
    """
    settings = get_settings()
    docs_path = docs_path or settings.docs_path

    # Resolve path relative to backend directory
    if not os.path.isabs(docs_path):
        base_dir = Path(__file__).parent.parent.parent
        docs_path = base_dir / docs_path

    docs_path = Path(docs_path).resolve()

    if not docs_path.exists():
        raise FileNotFoundError(f"Docs directory not found: {docs_path}")

    # Find all .md files
    md_files = list(docs_path.glob("*.md"))

    return [str(f) for f in md_files]


def process_all_docs(docs_path: str | None = None) -> list[dict]:
    """Process all markdown files into chunks with metadata.

    Args:
        docs_path: Path to docs directory

    Returns:
        List of chunk dictionaries with 'text', 'source', 'position', 'title' keys
    """
    all_chunks = []
    files = get_all_docs(docs_path)

    for filepath in files:
        try:
            parsed = parse_markdown_file(filepath)
            for position, chunk_text in enumerate(parsed["chunks"]):
                all_chunks.append(
                    {
                        "text": chunk_text,
                        "source": parsed["source"],
                        "position": position,
                        "title": parsed["title"],
                    }
                )
        except Exception as e:
            print(f"Error processing {filepath}: {e}")
            continue

    return all_chunks
