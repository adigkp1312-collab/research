"""
Configuration Management

Loads environment variables and provides typed configuration.
"""

from __future__ import annotations
import os
from functools import lru_cache
from typing import List
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # OpenRouter Configuration
    openrouter_api_key: str = ""
    openrouter_base_url: str = "https://openrouter.ai/api/v1"
    
    # LangSmith Configuration
    langchain_tracing_v2: bool = True
    langchain_api_key: str = ""
    langchain_project: str = "adiyogi-poc"
    
    # Pinecone Configuration (for future RAG)
    pinecone_api_key: str = ""
    pinecone_index: str = "adiyogi-knowledge"
    
    # Application Configuration
    app_name: str = "LangChain POC"
    debug: bool = True
    cors_origins: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Export settings instance
settings = get_settings()
