"""
LangChain Client Configuration

Direct Gemini 3 Flash API integration.
Matches main codebase pattern: direct os.environ.get() calls.
Pattern matches: backend/lambda/handlers/gemini.py
"""

from __future__ import annotations
import os
from typing import Optional, List
from langchain_google_genai import ChatGoogleGenerativeAI
from .config import (
    GEMINI_API_KEY,
    LANGCHAIN_TRACING_V2,
    LANGCHAIN_API_KEY,
    LANGCHAIN_PROJECT,
)

# Only Gemini 3 Flash
GEMINI_MODEL = "gemini-2.0-flash-exp"  # Latest Gemini 3 Flash


def create_chat_model(
    temperature: float = 0.7,
    streaming: bool = True,
    max_tokens: Optional[int] = None,
    callbacks: Optional[List] = None,
) -> ChatGoogleGenerativeAI:
    """
    Creates a LangChain ChatModel for Gemini 3 Flash.
    
    Matches main codebase pattern: backend/lambda/handlers/gemini.py
    Reads GEMINI_API_KEY from Lambda environment variables.
    
    Args:
        temperature: Sampling temperature (0-2)
        streaming: Whether to stream responses
        max_tokens: Maximum tokens in response
        callbacks: LangChain callbacks for streaming/tracing
    
    Returns:
        A configured ChatGoogleGenerativeAI instance
    
    Raises:
        ValueError: If GEMINI_API_KEY is not set in Lambda environment
    
    Example:
        >>> model = create_chat_model()
        >>> response = await model.ainvoke("Hello!")
    """
    
    # Direct access - matches main codebase pattern
    # Pattern: GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
    if not GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY not found in Lambda environment variables. "
            "Set it in Lambda configuration: "
            "aws lambda update-function-configuration "
            "--function-name YOUR_FUNCTION "
            "--environment Variables={GEMINI_API_KEY=your_key}"
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
        google_api_key=GEMINI_API_KEY,  # Direct constant access
    )
