"""
Conversation Chain Implementation

Creates a conversation chain with memory for the Director AI chat.
"""

import asyncio
from typing import AsyncGenerator, Callable
from langchain.chains import ConversationChain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.callbacks import AsyncIteratorCallbackHandler

from ..langchain_client import create_chat_model, MODELS
from ..memory import get_session_memory


# Director system prompt
DIRECTOR_SYSTEM_PROMPT = """You are a creative director for short-form video production at Adiyogi Arts.

Your role is to help users brainstorm, develop, and refine video concepts. You specialize in:
- Story development and narrative structure
- Visual storytelling and shot composition
- Character development and dialogue
- Mood, tone, and emotional themes
- Indian mythology and cultural elements

Guidelines:
1. Be creative but practical - suggestions should be achievable
2. Ask clarifying questions to understand the user's vision
3. Offer specific, actionable suggestions
4. Consider the target audience and platform
5. Balance artistic vision with production constraints

Keep responses concise and focused. When appropriate, structure your output for easy parsing."""


def create_director_chain(
    session_id: str,
    model_id: str = MODELS["GEMINI_FLASH"],
    system_prompt: str = DIRECTOR_SYSTEM_PROMPT,
    window_size: int = 10,
    callbacks: list | None = None,
) -> ConversationChain:
    """
    Creates a Director conversation chain with memory.
    
    Args:
        session_id: Unique session identifier
        model_id: OpenRouter model ID
        system_prompt: Custom system prompt
        window_size: Number of messages to keep in memory
        callbacks: LangChain callbacks for streaming
    
    Returns:
        ConversationChain with memory
    """
    # Create the chat model
    model = create_chat_model(
        model_id=model_id,
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
        verbose=True,  # Enable for debugging
    )


async def quick_chat(
    session_id: str,
    message: str,
    model_id: str = MODELS["GEMINI_FLASH"],
) -> str:
    """
    Simple wrapper for quick chat without streaming.
    
    Args:
        session_id: Session identifier
        message: User message
        model_id: Optional model override
    
    Returns:
        AI response text
    """
    chain = create_director_chain(session_id, model_id)
    result = await chain.ainvoke({"input": message})
    return result["response"]


async def stream_chat(
    session_id: str,
    message: str,
    model_id: str = MODELS["GEMINI_FLASH"],
) -> AsyncGenerator[str, None]:
    """
    Streaming chat that yields tokens as they arrive.
    
    Args:
        session_id: Session identifier
        message: User message
        model_id: Optional model override
    
    Yields:
        Tokens as they are generated
    """
    callback = AsyncIteratorCallbackHandler()
    
    chain = create_director_chain(
        session_id=session_id,
        model_id=model_id,
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
