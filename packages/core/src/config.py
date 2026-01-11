"""
Configuration Management

Centralized configuration for all packages.
Direct os.environ.get() calls - matches main codebase pattern.

Team: Platform
"""

import os

# =============================================================================
# VERTEX AI CONFIGURATION
# =============================================================================
GOOGLE_CLOUD_PROJECT = os.environ.get('GOOGLE_CLOUD_PROJECT', '')
VERTEX_AI_LOCATION = os.environ.get('VERTEX_AI_LOCATION', 'us-central1')

# =============================================================================
# LANGSMITH CONFIGURATION (Optional - Observability)
# =============================================================================
LANGCHAIN_TRACING_V2 = os.environ.get('LANGCHAIN_TRACING_V2', 'false').lower() == 'true'
LANGCHAIN_API_KEY = os.environ.get('LANGCHAIN_API_KEY', '')
LANGCHAIN_PROJECT = os.environ.get('LANGCHAIN_PROJECT', 'adiyogi-poc')

# =============================================================================
# VERTEX AI DATASTORE CONFIGURATION (RAG)
# =============================================================================
VERTEX_AI_DATASTORE_ID = os.environ.get('VERTEX_AI_DATASTORE_ID', '')
VERTEX_AI_DATASTORE_NAME = os.environ.get('VERTEX_AI_DATASTORE_NAME', 'adiyogi-knowledge-base')
VERTEX_AI_DATASTORE_DESCRIPTION = os.environ.get('VERTEX_AI_DATASTORE_DESCRIPTION', 'Knowledge base for rules and documentation')
GCS_BUCKET_NAME = os.environ.get('GCS_BUCKET_NAME', '')
RAG_TOP_K = int(os.environ.get('RAG_TOP_K', '5'))
RAG_CHUNK_SIZE = int(os.environ.get('RAG_CHUNK_SIZE', '1000'))
RAG_CHUNK_OVERLAP = int(os.environ.get('RAG_CHUNK_OVERLAP', '200'))

# =============================================================================
# VERTEX AI AGENT BUILDER / DATASTORE
# =============================================================================
VERTEX_AI_DATASTORE_ID = os.environ.get('VERTEX_AI_DATASTORE_ID', '')
VERTEX_AI_DATASTORE_LOCATION = os.environ.get('VERTEX_AI_DATASTORE_LOCATION', 'global')

# =============================================================================
# GOOGLE CLOUD STORAGE
# =============================================================================
GCS_BUCKET_NAME = os.environ.get('GCS_BUCKET_NAME', '')
GCS_UPLOAD_PREFIX = os.environ.get('GCS_UPLOAD_PREFIX', 'knowledge-base/uploads')

# =============================================================================
# RAG CONFIGURATION
# =============================================================================
RAG_ENABLED = os.environ.get('RAG_ENABLED', 'true').lower() == 'true'
RAG_TOP_K = int(os.environ.get('RAG_TOP_K', '5'))
RAG_CHUNK_SIZE = int(os.environ.get('RAG_CHUNK_SIZE', '1000'))
RAG_CHUNK_OVERLAP = int(os.environ.get('RAG_CHUNK_OVERLAP', '200'))
RAG_MAX_CONTEXT_LENGTH = int(os.environ.get('RAG_MAX_CONTEXT_LENGTH', '4000'))


def validate_rag_config() -> bool:
    """Validate RAG configuration."""
    missing = []
    
    if RAG_ENABLED:
        if not VERTEX_AI_DATASTORE_ID:
            missing.append('VERTEX_AI_DATASTORE_ID')
        if not GCS_BUCKET_NAME:
            missing.append('GCS_BUCKET_NAME')
    
    if missing:
        import warnings
        warnings.warn(f"RAG enabled but missing config: {missing}")
    
    return len(missing) == 0


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
    
    if not GOOGLE_CLOUD_PROJECT:
        missing.append('GOOGLE_CLOUD_PROJECT')
    
    if missing:
        import warnings
        warnings.warn(
            f"Missing required environment variables: {missing}. "
            "Configure them in Cloud Run environment variables or GCP project settings."
        )
    
    return len(missing) == 0


def get_config_summary() -> dict:
    """Get a summary of current configuration (safe for logging)."""
    return {
        "vertex_ai_configured": bool(GOOGLE_CLOUD_PROJECT),
        "vertex_ai_location": VERTEX_AI_LOCATION,
        "datastore_configured": bool(VERTEX_AI_DATASTORE_ID),
        "gcs_bucket_configured": bool(GCS_BUCKET_NAME),
        "rag_top_k": RAG_TOP_K,
        "langsmith_enabled": LANGCHAIN_TRACING_V2 and bool(LANGCHAIN_API_KEY),
        "langsmith_project": LANGCHAIN_PROJECT,
        "debug": DEBUG,
        "cors_origins": CORS_ORIGINS,
    }
