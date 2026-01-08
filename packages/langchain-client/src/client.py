"""
LangChain Client - Gemini Model Factory

Creates LangChain ChatModel instances for Gemini 3 Flash.

Team: AI/ML
"""

from __future__ import annotations
import os
from typing import Optional, List, Any

from langchain_google_genai import ChatGoogleGenerativeAI

# Import from core package
import sys
sys.path.insert(0, str(__file__).replace('/packages/langchain-client/src/client.py', ''))
from packages.core.src import (
    GEMINI_API_KEY,
    LANGCHAIN_TRACING_V2,
    LANGCHAIN_API_KEY,
    LANGCHAIN_PROJECT,
)

# Model Configuration
GEMINI_MODEL = "gemini-2.0-flash-exp"
MODEL_NAME = "Gemini 3 Flash (Experimental)"


def create_chat_model(
    temperature: float = 0.7,
    streaming: bool = True,
    max_tokens: Optional[int] = None,
    callbacks: Optional[List[Any]] = None,
) -> ChatGoogleGenerativeAI:
    """
    Creates a LangChain ChatModel for Gemini 3 Flash.
    
    Args:
        temperature: Sampling temperature (0-2)
        streaming: Whether to stream responses
        max_tokens: Maximum tokens in response
        callbacks: LangChain callbacks for streaming/tracing
    
    Returns:
        A configured ChatGoogleGenerativeAI instance
    
    Raises:
        ValueError: If GEMINI_API_KEY is not set
    
    Example:
        >>> model = create_chat_model()
        >>> response = await model.ainvoke("Hello!")
    """
    if not GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY not found in environment variables. "
            "Set it in Lambda configuration or local .env file."
        )
    
    # Configure LangSmith tracing (optional)
    if LANGCHAIN_TRACING_V2 and LANGCHAIN_API_KEY:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_API_KEY"] = LANGCHAIN_API_KEY
        os.environ["LANGCHAIN_PROJECT"] = LANGCHAIN_PROJECT
    
    return ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        temperature=temperature,
        streaming=streaming,
        max_tokens=max_tokens,
        callbacks=callbacks,
        google_api_key=GEMINI_API_KEY,
    )


def get_model_info() -> dict:
    """Get information about the current model."""
    return {
        "model": GEMINI_MODEL,
        "model_name": MODEL_NAME,
        "provider": "Google",
        "api_type": "Direct (via GEMINI_API_KEY)",
    }
