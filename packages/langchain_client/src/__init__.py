"""
LangChain Client Package - Gemini Model Factory

Creates and configures LangChain chat models for Gemini.

Team: AI/ML
"""

from .client import (
    create_chat_model,
    GEMINI_MODEL,
    MODEL_NAME,
)

__all__ = [
    "create_chat_model",
    "GEMINI_MODEL",
    "MODEL_NAME",
]
