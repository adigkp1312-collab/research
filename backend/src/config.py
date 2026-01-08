"""
Configuration Management

Optimized for Lambda environment variables.
Reads GEMINI_API_KEY from Lambda environment (os.environ).
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
    """Application settings - optimized for Lambda environment variables."""
    
    # Gemini API Key - MUST be set in Lambda environment variables
    # Lambda automatically injects GEMINI_API_KEY from environment
    gemini_api_key: str = ""
    
    # LangSmith Configuration (optional)
    langchain_tracing_v2: bool = False
    langchain_api_key: str = ""
    langchain_project: str = "adiyogi-poc"
    
    # Application Configuration
    app_name: str = "LangChain POC - Gemini 3 Flash"
    debug: bool = False  # Set to False in Lambda
    cors_origins: List[str] = ["*"]  # Lambda handles CORS
    
    class Config:
        # Lambda doesn't use .env files, so don't load them
        env_file = None
        env_file_encoding = "utf-8"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Lambda provides environment variables directly
        # os.environ.get works automatically in Lambda
        if not self.gemini_api_key:
            self.gemini_api_key = os.environ.get("GEMINI_API_KEY", "")
        
        # Validate key is set (will fail fast in Lambda if not configured)
        if not self.gemini_api_key:
            import warnings
            warnings.warn(
                "GEMINI_API_KEY not found in Lambda environment variables. "
                "Configure it in Lambda console or via AWS CLI."
            )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Export settings instance
settings = get_settings()
