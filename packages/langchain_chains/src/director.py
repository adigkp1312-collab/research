"""
Director Chain - Video Production Assistant

Direct Vertex AI conversation for the Director AI chat.

Team: AI/ML
"""

from __future__ import annotations
from typing import AsyncGenerator, Optional

# Import from sibling packages
# PYTHONPATH is set by handler.py or main.py entry point
from packages.langchain_client.src import create_chat_model
from packages.langchain_memory.src import get_session_memory

from .prompts import DIRECTOR_SYSTEM_PROMPT

# RAG imports (optional - graceful degradation if not available)
try:
    from packages.knowledge_base.src import retrieve_context
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    retrieve_context = None


def _build_conversation_prompt(
    system_prompt: str,
    history: list,
    user_message: str,
    rag_context: str = "",
) -> str:
    """
    Build conversation prompt for Vertex AI with optional RAG context.
    
    Vertex AI's GenerativeModel.generate_content() accepts a string prompt.
    We format the conversation history as part of the prompt.
    
    Args:
        system_prompt: System prompt text
        history: List of message dicts with "role" and "content"
        user_message: Current user message
        rag_context: Optional RAG context from knowledge base
    
    Returns:
        Formatted prompt string
    """
    # Start with system prompt
    prompt_parts = [system_prompt, "\n\n"]
    
    # Add RAG context if available
    if rag_context:
        prompt_parts.append(rag_context)
        prompt_parts.append("\n\n")
    
    # Add conversation history
    prompt_parts.append("## Conversation History:\n")
    for msg in history:
        role_prefix = "User: " if msg["role"] == "user" else "Assistant: "
        prompt_parts.append(f"{role_prefix}{msg['content']}\n")
    
    # Add current user message
    prompt_parts.append(f"\nUser: {user_message}\n")
    prompt_parts.append("Assistant: ")
    
    return "".join(prompt_parts)


async def quick_chat(
    session_id: str,
    message: str,
    system_prompt: str = DIRECTOR_SYSTEM_PROMPT,
) -> str:
    """
    Simple wrapper for quick chat without streaming.
    
    Args:
        session_id: Session identifier
        message: User message
        system_prompt: Optional custom prompt
    
    Returns:
        AI response text
    """
    # Get memory for this session
    memory = get_session_memory(session_id)
    history = memory.get_messages()
    
    # Retrieve RAG context if available
    rag_context = ""
    if RAG_AVAILABLE and retrieve_context:
        try:
            rag_context = retrieve_context(message, top_k=5)
        except Exception:
            # Graceful degradation - continue without RAG
            rag_context = ""
    
    # Build conversation prompt with RAG context
    prompt = _build_conversation_prompt(system_prompt, history, message, rag_context)
    
    # Create model
    model = create_chat_model(temperature=0.7, streaming=False)
    
    # Generate response
    response = model.generate_content(prompt)
    
    # Extract text from response
    response_text = response.text if hasattr(response, 'text') else str(response)
    
    # Save to memory
    memory.save_context({"input": message}, {"output": response_text})
    
    return response_text


async def stream_chat(
    session_id: str,
    message: str,
    system_prompt: str = DIRECTOR_SYSTEM_PROMPT,
) -> AsyncGenerator[str, None]:
    """
    Streaming chat that yields tokens as they arrive.
    
    Args:
        session_id: Session identifier
        message: User message
        system_prompt: Optional custom prompt
    
    Yields:
        Tokens as they are generated
    
    Example:
        >>> async for token in stream_chat("session-1", "Hello"):
        ...     print(token, end="")
    """
    # Get memory for this session
    memory = get_session_memory(session_id)
    history = memory.get_messages()
    
    # Retrieve RAG context if available
    rag_context = ""
    if RAG_AVAILABLE and retrieve_context:
        try:
            rag_context = retrieve_context(message, top_k=5)
        except Exception:
            # Graceful degradation - continue without RAG
            rag_context = ""
    
    # Build conversation prompt with RAG context
    prompt = _build_conversation_prompt(system_prompt, history, message, rag_context)
    
    # Create model with streaming
    model = create_chat_model(temperature=0.7, streaming=True)
    
    # Generate response with streaming
    response = model.generate_content(prompt, stream=True)
    
    # Collect full response for memory
    full_response = ""
    
    # Yield tokens as they arrive
    for chunk in response:
        if hasattr(chunk, 'text') and chunk.text:
            token = chunk.text
            full_response += token
            yield token
        elif hasattr(chunk, 'parts'):
            for part in chunk.parts:
                if hasattr(part, 'text') and part.text:
                    token = part.text
                    full_response += token
                    yield token
    
    # Save to memory after streaming completes
    memory.save_context({"input": message}, {"output": full_response})
