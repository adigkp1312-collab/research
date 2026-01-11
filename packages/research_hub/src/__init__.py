"""
Research Hub - Unified research platform for branding and marketing intelligence.

This package provides multi-agent research capabilities using Vertex AI Agent Garden tools.
"""

from .orchestrator import ResearchOrchestrator
from .config import validate_research_hub_config

__all__ = [
    "ResearchOrchestrator",
    "validate_research_hub_config",
]
