"""
LangChain Client Package - Gemini Model Factory

Creates and configures LangChain chat models for Gemini.

Team: AI/ML
"""

from .client import (
    init_vertex_ai,
    create_chat_model,
    get_model_info,
    GEMINI_MODEL,
    MODEL_NAME,
)

__all__ = [
    "init_vertex_ai",
    "create_chat_model",
    "get_model_info",
    "GEMINI_MODEL",
    "MODEL_NAME",
]
