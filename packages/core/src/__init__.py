"""
Core Package - Shared utilities and configuration

This package provides shared configuration, types, and utilities
used by all other packages in the monorepo.

Team: Platform
"""

from .config import (
    GEMINI_API_KEY,
    GEMINI_BASE_URL,
    LANGCHAIN_TRACING_V2,
    LANGCHAIN_API_KEY,
    LANGCHAIN_PROJECT,
    APP_NAME,
    DEBUG,
    CORS_ORIGINS,
    validate_config,
)

__all__ = [
    "GEMINI_API_KEY",
    "GEMINI_BASE_URL",
    "LANGCHAIN_TRACING_V2",
    "LANGCHAIN_API_KEY",
    "LANGCHAIN_PROJECT",
    "APP_NAME",
    "DEBUG",
    "CORS_ORIGINS",
    "validate_config",
]
