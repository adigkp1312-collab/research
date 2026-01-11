"""
Configuration for the Research Hub.

All configuration is loaded from environment variables following the project's
cloud-native configuration pattern.
"""

import os
from typing import Dict, List


# =============================================================================
# GOOGLE CLOUD CONFIGURATION
# =============================================================================

GOOGLE_CLOUD_PROJECT = os.environ.get('GOOGLE_CLOUD_PROJECT', '')
VERTEX_AI_LOCATION = os.environ.get('VERTEX_AI_LOCATION', 'us-central1')

# =============================================================================
# FIRESTORE CONFIGURATION
# =============================================================================

# Firestore uses the same GOOGLE_CLOUD_PROJECT
# Collection name for research entries
FIRESTORE_COLLECTION = os.environ.get('FIRESTORE_COLLECTION', 'research_hub_entries')

# =============================================================================
# MODEL CONFIGURATION
# =============================================================================

# Default model for research agents
DEFAULT_MODEL = os.environ.get('RESEARCH_HUB_MODEL', 'gemini-2.0-flash-001')

# Advanced model for complex analysis (optional upgrade)
ADVANCED_MODEL = os.environ.get('RESEARCH_HUB_ADVANCED_MODEL', 'gemini-1.5-pro-002')

# =============================================================================
# YOUTUBE API CONFIGURATION
# =============================================================================

YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY', '')

# =============================================================================
# META (FACEBOOK/INSTAGRAM) ADS API CONFIGURATION
# =============================================================================

# Option 1: Use a long-lived access token (recommended for production)
META_ACCESS_TOKEN = os.environ.get('META_ACCESS_TOKEN', '')

# Option 2: Use app credentials to generate tokens
META_APP_ID = os.environ.get('META_APP_ID', '')
META_APP_SECRET = os.environ.get('META_APP_SECRET', '')

# =============================================================================
# RAG CONFIGURATION
# =============================================================================

VERTEX_AI_DATASTORE_ID = os.environ.get('VERTEX_AI_DATASTORE_ID', '')
RAG_ENABLED = os.environ.get('RAG_ENABLED', 'true').lower() == 'true'
RAG_TOP_K = int(os.environ.get('RAG_TOP_K', '5'))

# =============================================================================
# RESEARCH HUB SETTINGS
# =============================================================================

# Timeout for individual research operations (seconds)
RESEARCH_TIMEOUT_SECONDS = int(os.environ.get('RESEARCH_TIMEOUT_SECONDS', '60'))

# Maximum concurrent agents for parallel research
MAX_CONCURRENT_AGENTS = int(os.environ.get('MAX_CONCURRENT_AGENTS', '3'))

# Enable agent execution tracing for debugging
ENABLE_AGENT_TRACING = os.environ.get('ENABLE_AGENT_TRACING', 'false').lower() == 'true'

# Cache TTL for research results (hours)
CACHE_TTL_HOURS = int(os.environ.get('RESEARCH_CACHE_TTL_HOURS', '24'))

# =============================================================================
# CORS CONFIGURATION
# =============================================================================

CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')


def validate_research_hub_config() -> Dict[str, any]:
    """
    Validate Research Hub configuration.

    Returns:
        Dict with configuration status and any missing required variables.
    """
    status = {
        "vertex_ai": bool(GOOGLE_CLOUD_PROJECT),
        "firestore": bool(GOOGLE_CLOUD_PROJECT),  # Firestore uses same project
        "youtube": bool(YOUTUBE_API_KEY),
        "meta_ads": bool(META_ACCESS_TOKEN or (META_APP_ID and META_APP_SECRET)),
        "rag": bool(VERTEX_AI_DATASTORE_ID) if RAG_ENABLED else True,
    }

    missing: List[str] = []

    if not GOOGLE_CLOUD_PROJECT:
        missing.append("GOOGLE_CLOUD_PROJECT")

    # Optional API warnings
    warnings: List[str] = []
    if not YOUTUBE_API_KEY:
        warnings.append("YOUTUBE_API_KEY not set - Video/Ad analysis will be limited")

    if not META_ACCESS_TOKEN and not (META_APP_ID and META_APP_SECRET):
        warnings.append("META_ACCESS_TOKEN not set - Meta Ads analysis will be unavailable")

    if RAG_ENABLED and not VERTEX_AI_DATASTORE_ID:
        warnings.append("RAG_ENABLED but VERTEX_AI_DATASTORE_ID not set - RAG features disabled")

    return {
        "configured": status,
        "missing": missing,
        "warnings": warnings,
        "ready": len(missing) == 0 and status["vertex_ai"],
    }


def get_config_summary() -> Dict[str, any]:
    """
    Get a safe summary of configuration for logging.

    Returns:
        Dict with configuration summary (no secrets).
    """
    return {
        "project": GOOGLE_CLOUD_PROJECT[:10] + "..." if GOOGLE_CLOUD_PROJECT else None,
        "location": VERTEX_AI_LOCATION,
        "model": DEFAULT_MODEL,
        "storage": "firestore",
        "firestore_collection": FIRESTORE_COLLECTION,
        "youtube_configured": bool(YOUTUBE_API_KEY),
        "meta_ads_configured": bool(META_ACCESS_TOKEN or (META_APP_ID and META_APP_SECRET)),
        "rag_enabled": RAG_ENABLED and bool(VERTEX_AI_DATASTORE_ID),
        "timeout_seconds": RESEARCH_TIMEOUT_SECONDS,
        "max_concurrent_agents": MAX_CONCURRENT_AGENTS,
        "tracing_enabled": ENABLE_AGENT_TRACING,
    }
