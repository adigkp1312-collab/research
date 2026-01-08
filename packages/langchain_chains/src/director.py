"""
Director Chain - Video Production Assistant

Conversation chain for the Director AI chat.

Team: AI/ML
"""

from __future__ import annotations
import asyncio
from typing import AsyncGenerator, Optional, List, Any

from langchain.chains import ConversationChain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.callbacks import AsyncIteratorCallbackHandler

# Import from sibling packages
# PYTHONPATH is set by handler.py or main.py entry point
from packages.langchain_client.src import create_chat_model
from packages.langchain_memory.src import get_session_memory

from .prompts import DIRECTOR_SYSTEM_PROMPT


def create_director_chain(
    session_id: str,
    system_prompt: str = DIRECTOR_SYSTEM_PROMPT,
    window_size: int = 10,
    callbacks: Optional[List[Any]] = None,
) -> ConversationChain:
    """
    Creates a Director conversation chain with memory.
    
    Args:
        session_id: Unique session identifier
        system_prompt: Custom system prompt
        window_size: Number of messages to keep in memory
        callbacks: LangChain callbacks for streaming
    
    Returns:
        ConversationChain with memory
    
    Example:
        >>> chain = create_director_chain("user-123")
        >>> result = await chain.ainvoke({"input": "Help me brainstorm"})
    """
    # Create the chat model (Gemini 3 Flash)
    model = create_chat_model(
        temperature=0.7,
        streaming=True,
        callbacks=callbacks,
    )
    
    # Create the prompt template with system message and history
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}"),
    ])
    
    # Get or create memory for this session
    memory = get_session_memory(session_id, window_size)
    
    # Create and return the conversation chain
    return ConversationChain(
        llm=model,
        prompt=prompt,
        memory=memory,
        verbose=False,  # Set to False in production
    )


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
    chain = create_director_chain(session_id, system_prompt=system_prompt)
    result = await chain.ainvoke({"input": message})
    return result["response"]


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
    callback = AsyncIteratorCallbackHandler()
    
    chain = create_director_chain(
        session_id=session_id,
        system_prompt=system_prompt,
        callbacks=[callback],
    )
    
    # Run the chain in a background task
    async def run_chain():
        try:
            await chain.ainvoke({"input": message})
        except Exception as e:
            print(f"Chain error: {e}")
        finally:
            callback.done.set()
    
    task = asyncio.create_task(run_chain())
    
    # Yield tokens as they arrive
    async for token in callback.aiter():
        yield token
    
    # Wait for chain to complete
    await task
