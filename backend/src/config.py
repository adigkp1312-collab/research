"""
Configuration Management

Simple pattern matching main codebase.
Direct os.environ.get() calls - no Pydantic complexity.
Pattern matches: backend/lambda/handlers/gemini.py
"""

import os

# =============================================================================
# GEMINI API CONFIGURATION
# =============================================================================
# API Configuration (keys from Lambda env vars)
# Pattern matches: backend/lambda/handlers/gemini.py
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
GEMINI_BASE_URL = 'https://generativelanguage.googleapis.com/v1beta'

# =============================================================================
# LANGSMITH CONFIGURATION (Optional)
# =============================================================================
LANGCHAIN_TRACING_V2 = os.environ.get('LANGCHAIN_TRACING_V2', 'false').lower() == 'true'
LANGCHAIN_API_KEY = os.environ.get('LANGCHAIN_API_KEY', '')
LANGCHAIN_PROJECT = os.environ.get('LANGCHAIN_PROJECT', 'adiyogi-poc')

# =============================================================================
# APPLICATION CONFIGURATION
# =============================================================================
APP_NAME = "LangChain POC - Gemini 3 Flash"
DEBUG = False  # Set to False in Lambda
CORS_ORIGINS = ["*"]  # Lambda handles CORS


# =============================================================================
# VALIDATION
# =============================================================================
def validate_config():
    """Validate that required configuration is present."""
    missing = []
    if not GEMINI_API_KEY:
        missing.append('GEMINI_API_KEY')
    
    if missing:
        import warnings
        warnings.warn(
            f"Missing required environment variables: {missing}. "
            "Configure them in Lambda environment variables."
        )
    
    return len(missing) == 0
