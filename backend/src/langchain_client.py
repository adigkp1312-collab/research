"""
LangChain Client Configuration

Configures LangChain to use OpenRouter for multi-model access.
"""

from __future__ import annotations
import os
from typing import Optional, List
from langchain_openai import ChatOpenAI
from .config import settings

# Available models via OpenRouter
MODELS = {
    # Google Gemini models
    "GEMINI_FLASH": "google/gemini-flash-1.5",
    "GEMINI_PRO": "google/gemini-pro-1.5",
    
    # Anthropic Claude models
    "CLAUDE_SONNET": "anthropic/claude-3-sonnet-20240229",
    "CLAUDE_OPUS": "anthropic/claude-3-opus-20240229",
    
    # OpenAI models
    "GPT4_TURBO": "openai/gpt-4-turbo",
    "GPT4O": "openai/gpt-4o",
    
    # Fast/cheap options
    "MISTRAL_LARGE": "mistralai/mistral-large-latest",
    "LLAMA_70B": "meta-llama/llama-3-70b-instruct",
}


def create_chat_model(
    model_id: str = MODELS["GEMINI_FLASH"],
    temperature: float = 0.7,
    streaming: bool = True,
    max_tokens: Optional[int] = None,
    callbacks: Optional[List] = None,
) -> ChatOpenAI:
    """
    Creates a LangChain ChatModel configured to use OpenRouter.
    
    Args:
        model_id: The OpenRouter model ID (e.g., "google/gemini-flash-1.5")
        temperature: Sampling temperature (0-2)
        streaming: Whether to stream responses
        max_tokens: Maximum tokens in response
        callbacks: LangChain callbacks for streaming/tracing
    
    Returns:
        A configured ChatOpenAI instance
    
    Example:
        >>> model = create_chat_model(MODELS["GEMINI_FLASH"])
        >>> response = await model.ainvoke("Hello!")
    """
    
    # Configure LangSmith tracing
    if settings.langchain_tracing_v2:
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_API_KEY"] = settings.langchain_api_key
        os.environ["LANGCHAIN_PROJECT"] = settings.langchain_project
    
    return ChatOpenAI(
        model=model_id,
        temperature=temperature,
        streaming=streaming,
        max_tokens=max_tokens,
        callbacks=callbacks,
        openai_api_key=settings.openrouter_api_key,
        openai_api_base=settings.openrouter_base_url,
        default_headers={
            "HTTP-Referer": "https://adiyogi.art",
            "X-Title": "Adiyogi POC",
        },
    )


def get_fast_model(**kwargs) -> ChatOpenAI:
    """Quick helper for fast model (Gemini Flash)."""
    return create_chat_model(MODELS["GEMINI_FLASH"], **kwargs)


def get_reasoning_model(**kwargs) -> ChatOpenAI:
    """Quick helper for reasoning model (Gemini Pro)."""
    return create_chat_model(MODELS["GEMINI_PRO"], **kwargs)


def get_creative_model(**kwargs) -> ChatOpenAI:
    """Quick helper for creative model (Claude Sonnet)."""
    return create_chat_model(MODELS["CLAUDE_SONNET"], **kwargs)
