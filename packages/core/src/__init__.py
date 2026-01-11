"""
Core Package - Shared utilities and configuration

This package provides shared configuration, types, and utilities
used by all other packages in the monorepo.

Team: Platform
"""

from .config import (
    GOOGLE_CLOUD_PROJECT,
    VERTEX_AI_LOCATION,
    VERTEX_AI_DATASTORE_ID,
    VERTEX_AI_DATASTORE_NAME,
    VERTEX_AI_DATASTORE_DESCRIPTION,
    GCS_BUCKET_NAME,
    RAG_TOP_K,
    RAG_CHUNK_SIZE,
    RAG_CHUNK_OVERLAP,
    LANGCHAIN_TRACING_V2,
    LANGCHAIN_API_KEY,
    LANGCHAIN_PROJECT,
    APP_NAME,
    DEBUG,
    CORS_ORIGINS,
    validate_config,
    get_config_summary,
)

__all__ = [
    "GOOGLE_CLOUD_PROJECT",
    "VERTEX_AI_LOCATION",
    "VERTEX_AI_DATASTORE_ID",
    "VERTEX_AI_DATASTORE_NAME",
    "VERTEX_AI_DATASTORE_DESCRIPTION",
    "GCS_BUCKET_NAME",
    "RAG_TOP_K",
    "RAG_CHUNK_SIZE",
    "RAG_CHUNK_OVERLAP",
    "LANGCHAIN_TRACING_V2",
    "LANGCHAIN_API_KEY",
    "LANGCHAIN_PROJECT",
    "APP_NAME",
    "DEBUG",
    "CORS_ORIGINS",
    "validate_config",
    "get_config_summary",
]
