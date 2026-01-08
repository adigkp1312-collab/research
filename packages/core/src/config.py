"""
Configuration Management

Centralized configuration for all packages.
Direct os.environ.get() calls - matches main codebase pattern.

Team: Platform
"""

import os

# =============================================================================
# GEMINI API CONFIGURATION
# =============================================================================
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
GEMINI_BASE_URL = 'https://generativelanguage.googleapis.com/v1beta'

# =============================================================================
# LANGSMITH CONFIGURATION (Optional - Observability)
# =============================================================================
LANGCHAIN_TRACING_V2 = os.environ.get('LANGCHAIN_TRACING_V2', 'false').lower() == 'true'
LANGCHAIN_API_KEY = os.environ.get('LANGCHAIN_API_KEY', '')
LANGCHAIN_PROJECT = os.environ.get('LANGCHAIN_PROJECT', 'adiyogi-poc')

# =============================================================================
# APPLICATION CONFIGURATION
# =============================================================================
APP_NAME = "Adiyogi LangChain"
DEBUG = os.environ.get('DEBUG', 'false').lower() == 'true'
CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')


# =============================================================================
# VALIDATION
# =============================================================================
def validate_config() -> bool:
    """
    Validate that required configuration is present.
    
    Returns:
        True if all required config is set, False otherwise
    """
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


def get_config_summary() -> dict:
    """Get a summary of current configuration (safe for logging)."""
    return {
        "gemini_configured": bool(GEMINI_API_KEY),
        "langsmith_enabled": LANGCHAIN_TRACING_V2 and bool(LANGCHAIN_API_KEY),
        "langsmith_project": LANGCHAIN_PROJECT,
        "debug": DEBUG,
        "cors_origins": CORS_ORIGINS,
    }
