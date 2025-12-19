"""RAG (Retrieval-Augmented Generation) service for chatbot responses."""

import google.generativeai as genai

from app.config import get_settings
from app.services.embeddings import embed_text
from app.services.vectordb import search

# Initialize Gemini model lazily
_model = None


def get_chat_model():
    """Get or create Google Gemini model instance."""
    global _model
    if _model is None:
        settings = get_settings()
        genai.configure(api_key=settings.google_api_key)
        _model = genai.GenerativeModel(settings.chat_model)
    return _model


# System prompt for the chatbot
SYSTEM_PROMPT = """You are a helpful AI assistant for the Physical AI Textbook, an open-source curriculum for learning humanoid robotics with ROS 2, simulation, and AI.

Your role is to:
1. Answer questions about robotics concepts covered in the textbook
2. Explain ROS 2, URDF, motion control, and simulation topics
3. Help students understand complex concepts with clear explanations
4. Provide code examples when relevant
5. Guide learners through the curriculum

When answering:
- Use the provided context from the textbook to give accurate answers
- If the context doesn't contain enough information, say so honestly
- Keep explanations clear and accessible for learners
- Reference specific chapters or sections when relevant
- For code questions, provide practical examples

If the user has highlighted specific text, focus your answer on that selection while using the broader context for support.

Be encouraging and supportive - learning robotics is challenging but rewarding!"""


async def retrieve_context(
    query: str,
    selected_text: str | None = None,
    limit: int = 5,
) -> list[dict]:
    """Retrieve relevant context from the vector database.

    Args:
        query: User's question
        selected_text: Optional highlighted text for additional context
        limit: Maximum number of chunks to retrieve

    Returns:
        List of relevant document chunks
    """
    # If there's selected text, combine it with the query for better retrieval
    search_query = query
    if selected_text:
        search_query = f"{query}\n\nContext from highlighted text: {selected_text}"

    # Generate embedding for the search query
    query_vector = await embed_text(search_query)

    # Search for relevant chunks
    results = await search(
        query_vector=query_vector,
        limit=limit,
        score_threshold=0.3,  # Lower threshold for local embeddings
    )

    return results


def format_context(chunks: list[dict]) -> str:
    """Format retrieved chunks into context string for the LLM.

    Args:
        chunks: List of retrieved document chunks

    Returns:
        Formatted context string
    """
    if not chunks:
        return "No relevant context found in the textbook."

    context_parts = []
    for i, chunk in enumerate(chunks, 1):
        source = chunk.get("source", "Unknown")
        title = chunk.get("title", "")
        text = chunk.get("text", "")

        header = f"[Source {i}: {title} ({source})]"
        context_parts.append(f"{header}\n{text}")

    return "\n\n---\n\n".join(context_parts)


async def generate_response(
    query: str,
    context_chunks: list[dict],
    conversation_history: list[dict] | None = None,
    selected_text: str | None = None,
) -> str:
    """Generate a response using Google Gemini with RAG context.

    Args:
        query: User's question
        context_chunks: Retrieved context chunks
        conversation_history: Previous messages in the conversation
        selected_text: Optional highlighted text

    Returns:
        Generated response text
    """
    model = get_chat_model()

    # Format the context
    context = format_context(context_chunks)

    # Build the prompt with system instructions and context
    prompt_parts = [SYSTEM_PROMPT, "\n\n"]

    # Add conversation history (last few messages for context)
    if conversation_history:
        prompt_parts.append("Previous conversation:\n")
        recent_history = conversation_history[-6:]
        for msg in recent_history:
            role = "User" if msg["role"] == "user" else "Assistant"
            prompt_parts.append(f"{role}: {msg['content']}\n")
        prompt_parts.append("\n")

    # Add selected text if present
    if selected_text:
        prompt_parts.append(
            f"The user has highlighted the following text:\n```\n{selected_text}\n```\n\n"
        )

    # Add the question and context
    prompt_parts.append(f"Question: {query}\n\n")
    prompt_parts.append(f"Relevant context from the textbook:\n{context}\n\n")
    prompt_parts.append("Please provide a helpful answer based on the context above.")

    full_prompt = "".join(prompt_parts)

    # Generate response using Gemini
    response = model.generate_content(full_prompt)

    return response.text


async def chat(
    query: str,
    session_id: str,
    selected_text: str | None = None,
    conversation_history: list[dict] | None = None,
) -> tuple[str, list[dict]]:
    """Main chat function that orchestrates RAG retrieval and generation.

    Args:
        query: User's question
        session_id: Session ID for context
        selected_text: Optional highlighted text
        conversation_history: Previous conversation messages

    Returns:
        Tuple of (response text, source references)
    """
    # Retrieve relevant context
    context_chunks = await retrieve_context(
        query=query,
        selected_text=selected_text,
        limit=5,
    )

    # Generate response
    response = await generate_response(
        query=query,
        context_chunks=context_chunks,
        conversation_history=conversation_history,
        selected_text=selected_text,
    )

    # Format sources for response
    sources = [
        {
            "file": chunk.get("source", ""),
            "chunk": chunk.get("text", "")[:200] + "..."
            if len(chunk.get("text", "")) > 200
            else chunk.get("text", ""),
            "score": chunk.get("score"),
        }
        for chunk in context_chunks
    ]

    return response, sources
