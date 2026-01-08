"""
LangChain Chains Package - Conversation Logic

Implements conversation chains for different use cases.

Team: AI/ML
"""

from .director import (
    create_director_chain,
    quick_chat,
    stream_chat,
    DIRECTOR_SYSTEM_PROMPT,
)
from .prompts import PROMPTS

__all__ = [
    "create_director_chain",
    "quick_chat",
    "stream_chat",
    "DIRECTOR_SYSTEM_PROMPT",
    "PROMPTS",
]
